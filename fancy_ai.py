import json
from openai import OpenAI
from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC

# dotenv for openai key

from dotenv import load_dotenv
load_dotenv()


class CalendarAssistant:
    def __init__(self, calendar: Calendar = Calendar()):
        self.client = OpenAI()
        self.messages = []
        self.tools = []

        # this is a dictionary of functions that the AI can call
        self.available_functions = {"add_event_to_calendar": add_event_to_calendar}

        self.calendar = calendar  # start with a blank calendar

        self.messages = [
            {
                "role": "system",
                # todo: make current year next year next year
                "content": f"You are a calendar-creating assistant. Take the input text and generate a calendar. The current year is 2024.",
            },
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "add_event_to_calendar",
                    # todo: figure out the right prompt for this
                    "description": "Add a new event to the existing calendar. Enter times in the calendar's timezone.",
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
                                "type": "string",  # datetime parsing stuff necessary
                                "description": "The time the event starts.",
                            },
                            "end_time": {
                                "type": "string",  # datetime parsing stuff necessary
                                "description": "The time the event starts.",
                            },
                            "location": {
                                "type": "string",
                                "description": "The location of the event. Optional.",
                            },
                            # should this even be given to the ai? maybe just have it as a default value specified by the user
                            # guessing whose email to use is kinda stupid
                            # "organizer_email": {
                            #     "type": "string",
                            #     "description": "The email of the event organizer. Optional.",
                            # },
                            # todo: add other stuff so it matches
                        },
                        "required": ["summary", "start_time", "end_time"],
                    },
                },
            },
        ]

    def query_ai(
        self,
        prompt: str,
        role="user",
    ):
        # TODO: use streaming to make it faster / more responsive
        self.messages.append({"role": role, "content": prompt})
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",
            parallel_tool_calls=True,  # TODO test this, could be handy
        )
        return response

    def handle_user_message(self, message: str):
        response = self.query_ai(message)
        top_response = response.choices[0].message

        tool_calls = top_response.tool_calls
        if tool_calls is not None:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = self.available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                try:
                    print(
                        f"Calling function `{function_name}` with args `{function_args}`"
                    )
                    if function_to_call is not None:
                        if function_to_call == add_event_to_calendar:
                            # add the event to the existing calendar
                            parsed_args = parse_ai_function_args(function_args)
                            add_event_to_calendar(self.calendar, **parsed_args)
                        else:
                            function_to_call(**function_args)
                except:  # probably a value error tbh
                    print(
                        f"Error calling function `{function_name}` with args `{function_args}`"
                    )
                    continue
        if top_response.content is not None:
            # non-function text output from the AI
            # figure out how to display this/what to do with it
            print(top_response.content)
        else:
            print("Bing bong! No text content in response")


def parse_ai_function_args(args: dict) -> dict:
    # convert the string datetime to a datetime object
    args["start_time"] = datetime.fromisoformat(args["start_time"])
    args["end_time"] = datetime.fromisoformat(args["end_time"])
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
) -> str:
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
    event.add("summary", summary)
    event.add("dtstart", start_time)
    event.add("dtend", end_time)

    event.add(
        "dtstamp", datetime.now(UTC)
    )  # used for when the event was added to the calendar

    if description:
        event.add("description", description)
    if location:
        event.add("location", location)
    if organizer_email:
        event.add("organizer", organizer_email)

    # maybe add some validation here?
    # to remove any obviously incorrect events, e.g. end_time < start_time
    if end_time < start_time:
        return "Error: end time is before start time."
    calendar.add_component(event)

    # Convert the calendar to string in iCalendar format
    # can use this return value if you want
    return calendar.to_ical().decode("utf-8")


# Example usage
# start_time = datetime(2024, 10, 1, 10, 0, tzinfo=UTC)  # Event start time
# end_time = datetime(2024, 10, 1, 11, 0, tzinfo=UTC)  # Event end time

# cal = Calendar()

# calendar_data = add_event_to_calendar(
#     calendar=cal,
#     summary="Team Meeting",
#     description="Discussion on project progress",
#     location="Conference Room 1",
#     start_time=start_time,
#     end_time=end_time,
#     organizer_email="organizer@example.com",
# )

# print(cal.to_ical().decode("utf-8"))
# print(calendar_data)

# Write the calendar data to a file
# with open("meeting.ics", "w") as f:
#     f.write(calendar_data)

example_str = """
Sep 12 - OS Shell Assignment Released
Sep 17 - Scheduling Assignment Released
Oct 3 - Virtual Memory (2/3)
Oct 10 - Mid-semester Q&A (no lab)
Oct 15 - Graded Exercises Released
Oct 18 - A1 Graded
Oct 24 - OS Shell Assignment Due
Oct 25 - A2 Graded
Nov 7 - Gradied Exercises Due
Nov 14 - Exercises Graded
Nov 28 - A3 Graded
Dec 3 - End-of-Semester Q&A (Final class)
Dec 6 - Last class
Dec 8 - Memory Management Assign. Due
Dec 9 - A4 Graded
Dec 14 - Midterm Exam Grade Posted
"""

cal_assistant = CalendarAssistant()

# take this hsit and turn it into a calendar. should parse the whole thing as one chunk.
x = cal_assistant.handle_user_message(example_str)

cal_txt = cal_assistant.calendar.to_ical().decode("utf-8")

with open("calendar.ics", "w") as f:
    f.write(cal_txt)