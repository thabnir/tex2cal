import json
from openai import OpenAI
from icalendar import Calendar, Event
from datetime import datetime
from zoneinfo import ZoneInfo
from pytz import UTC
from dotenv import load_dotenv


# dotenv for openai key
load_dotenv()


class CalendarAssistant:
    def __init__(self, calendar: Calendar = Calendar()):
        self.client = OpenAI()
        self.messages = []
        self.tools = []

        # this is a dictionary of functions that the AI can call
        self.available_functions = {
            "add_event_to_calendar": add_event_to_calendar,
            "set_calendar_name": self.set_calendar_name,
        }

        self.calendar = calendar  # start with a blank calendar
        self.calendar_name = (
            "ai_calendar"  # default name for the calendar if the ai doesn't set one
        )

        self.timezone = ZoneInfo("America/New_York")  # default to eastern time
        today = (
            datetime.today().astimezone(self.timezone).strftime("%A, %B %d, %Y - %H:%M")
        )  # Weekday, Month Day, Year

        # context = "the user's existing calendar. TODO: figure out how to get the user's existing calendar"

        self.messages = [
            {
                "role": "system",
                # Assumes the events are in the same timezone as the calendar, which is the user's timezone.
                # This is not necessarily true, but it's a reasonable assumption most of the time.
                "content": f"You are a calendar-creating assistant. Generate a calendar including all events in the input and be sure to give it a useful name. It is {today}, and, all calendar events should be assumed to be near this date (only 2024 or later).",
            },
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_event_to_calendar",
                    # todo: figure out the right prompt for this
                    "description": "Add a new event to the existing calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "summary": {
                                "type": "string",
                                "description": "The name of the event to add to the calendar.",
                            },
                            "description": {
                                "type": "string",
                                "description": "A description of the event. Optional.",
                            },
                            "start_time": {
                                "type": "string",
                                "description": "The time the event starts. Format in ISO 8601.",
                            },
                            "end_time": {
                                "type": "string",
                                "description": "The time the event starts. Format in ISO 8601.",
                            },
                            "location": {
                                "type": "string",
                                "description": "The location of the event. Optional.",
                            },
                        },
                        "required": ["summary", "start_time", "end_time"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "set_calendar_name",
                    "description": "Set the name of the calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the calendar.",
                            },
                        },
                        "required": ["name"],
                    },
                },
            },
        ]

    def set_calendar_name(self, name: str):
        self.calendar_name = name

    def query_ai(
        self,
        prompt: str,
        role="user",
    ):
        self.messages.append({"role": role, "content": prompt})
        print(f"Querying AI with messages: {self.messages}")
        response = self.client.chat.completions.create(
            model="gpt-4o",  # TODO: see if i can get away with using a smaller model so it's faster
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",
            parallel_tool_calls=True,
        )
        return response

    def handle_user_message(self, message: str) -> str:
        response = self.query_ai(message)
        top_response = response.choices[0].message

        tool_calls = top_response.tool_calls
        if tool_calls is not None:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                try:
                    print(f"Calling {function_name}({function_args})...")
                    if function_to_call is not None:
                        if function_to_call == add_event_to_calendar:
                            # add the event to the existing calendar
                            parsed_args = self.parse_ai_function_args(function_args)
                            add_event_to_calendar(self.calendar, **parsed_args)
                        else:
                            function_to_call(**function_args)
                except Exception as e:  # probably a value error tbh
                    print(
                        f"Error calling {function_name}({function_args}) with error: {e}"
                    )
                    continue
        if top_response.content is not None:
            # non-function text output from the AI
            # figure out how to display this/what to do with it / what to ask the ai to even write here if anything
            # print(top_response.content)
            return top_response.content
        else:
            print("No text content in AI response. The calendar speaks for itself!")
            return ""

    def write_calendar(self, filename: str | None = None):
        ical_string = self.to_ical_string()
        if filename is None:
            filename = f"{self.calendar_name}.ics"
        with open(filename, "w") as f:
            f.write(ical_string)

    def to_ical_string(self) -> str:
        return self.calendar.to_ical().decode("utf-8")

    def to_ical_bytes(self) -> bytes:
        return self.calendar.to_ical()

    def parse_ai_function_args(self, args: dict) -> dict:
        # convert the string datetime to a datetime object
        start_time = datetime.fromisoformat(args["start_time"])
        end_time = datetime.fromisoformat(args["end_time"])

        if end_time < start_time:
            print(
                f"Error: end time is before start time for event {args['summary']} from start={start_time} to end={end_time}"
            )
            # pretend like everything is ok if you switch them around (this is a bad idea but it won't crash)
            temp = start_time
            start_time = end_time
            end_time = temp

        # convert the datetime objects to the user's timezone
        # e.g. given a datetime object specifying 7pm in UTC, convert it to 7pm in the user's timezone
        start_time = start_time.astimezone(self.timezone)
        end_time = end_time.astimezone(self.timezone)

        print(
            f"Event {args['summary']} from {start_time.strftime('(%A, %B %d, %Y %I:%M %p)')} to {end_time.strftime('(%A, %B %d, %Y %I:%M %p)')}"
        )

        args["start_time"] = start_time
        args["end_time"] = end_time
        return args


# TODO: make sure that it doesn't copy the calendar every time, and instead modifies the input calendar in place
def add_event_to_calendar(
    calendar: Calendar,
    summary: str,
    start_time: datetime,
    end_time: datetime,
    description: str = "",
    location: str = "",
    organizer_email: str = "",
):
    """
    Adds an event to the calendar. Returns a string representation of the calendar in iCalendar format.

    Parameters:
        calendar (Calendar): The calendar to add the event to.
        summary (str): The summary or title of the event.
        start_time (datetime): The start time of the event.
        end_time (datetime): The end time of the event.
        description (str, optional): The description of the event. Defaults to an empty string.
        location (str, optional): The location of the event. Defaults to an empty string.
        organizer_email (str, optional): The email address of the event organizer. Defaults to an empty string.

    Returns:
        str: The calendar in iCalendar format as a string.
    """
    event = Event()

    # Localize the datetime objects to UTC
    event["X-DT-PYTZ"] = UTC.localize(datetime.now())

    event.add("summary", summary)
    event.add("dtstart", start_time)
    event.add("dtend", end_time)

    # used for when the event was added to the calendar
    event.add("dtstamp", datetime.now())

    if description:
        event.add("description", description)
    if location:
        event.add("location", location)
    if organizer_email:
        event.add("organizer", organizer_email)

    calendar.add_component(event)