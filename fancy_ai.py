import base64
import json
import random
import openai
from openai import OpenAI
from io import BytesIO
from typing import List
from icalendar import Calendar, Event
from datetime import datetime
from pytz import UTC  # timezone handling


class CalendarAssistant:
    def __init__(self):
        # name, class
        self.users: List[tuple[str, str]] = []
        self.client: OpenAI
        self.messages = []

        self.content = []  # contains story content + images in base64 in order + with character labels

        self.tools = []

        self.character_1_health: int
        self.character_1_class: str
        self.character_1_name: str

        self.character_2_health: int
        self.character_2_class: str
        self.character_2_name: str

        self.is_started: bool = False

    def get_messages(self):
        return self.messages

    def get_last_message(self):
        return self.messages[-1]

    def setup(self):
        # this should probably inside the constructor
        self.client = OpenAI()

        self.available_functions = {"deal_damage": self.deal_damage}
        self.messages = [
            {
                "role": "system",
                "content": f"You are a calendar-creating assistant. Take the input text and generate a calendar.",
            },
        ]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "deal_damage",
                    "description": "Deal the specified integer damage value to character `name.` Max health is 100",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",  # TODO: check if this should be an ID instead of a name. Tests needed
                                "description": "The name of the character whose health value is being updated",
                            },
                            "damage_amount": {
                                "type": "integer",
                                "description": "The amount the character's health is being decreased by. Negative values will increase the character's health.",
                            },
                        },
                        "required": ["name", "damage_amount"],
                    },
                },
            },
        ]

        prompt = ""

    def generate_story(
        self,
        prompt: str,
        role="user",
    ):
        self.messages.append({"role": role, "content": prompt})
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.messages,
            tools=self.tools,
            tool_choice="auto",
        )
        return response

    def deal_damage(self, name: str, damage_amount: int):
        if name == self.character_1_name:
            self.character_1_health -= damage_amount
        elif name == self.character_2_name:
            self.character_2_health -= damage_amount
        else:
            raise ValueError(f"Character name {name} not found")
        print(f"{name} took {damage_amount} damage")
        # print heatlh
        print(f"{self.character_1_name} has {self.character_1_health} health")
        print(f"{self.character_2_name} has {self.character_2_health} health")
        if self.character_1_health <= 0:
            print(f"{self.character_1_name} has been defeated!")
            return self.character_2_name
        elif self.character_2_health <= 0:
            print(f"{self.character_2_name} has been defeated!")
            return self.character_1_name

    def user_submit_message(self, message: str, char_name: str):
        prompt = f"{char_name}: {message} [HIDDEN SYSTEM MESSAGE: ROLLED A {random.randint(1, 20)}]"  # TODO: remove the random roll or make it visible to the user
        userContent = {
            "name": char_name,
            "content": message,
            "base64_image": None,
        }
        self.content.append(userContent)

        response = self.generate_story(prompt)
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
                    function_to_call(**function_args)
                except:  # probably a value error tbh
                    print(
                        f"Error calling function `{function_name}` with args `{function_args}`"
                    )
                    continue
        if top_response.content is not None:
            b64_img = self.generate_image_multitry_content(top_response.content)
            narratorContent = {
                "name": "Narrator",
                "content": top_response.content,
                "base64_image": b64_img,
            }
            self.content.append(narratorContent)
        else:
            print("ERROR: No content generated")

def create_calendar_event(summary, description, location, start_time, end_time, organizer_email):
    # Create a new calendar
    cal = Calendar()

    # Create a new event
    event = Event()
    event.add('summary', summary)
    event.add('description', description)
    event.add('location', location)
    event.add('dtstart', start_time)
    event.add('dtend', end_time)
    event.add('dtstamp', datetime.now(UTC))
    event.add('organizer', organizer_email)

    # Add event to calendar
    cal.add_component(event)

    # Convert the calendar to string in iCalendar format
    return cal.to_ical().decode('utf-8')

# Example usage
start_time = datetime(2024, 10, 1, 10, 0, tzinfo=UTC)  # Event start time
end_time = datetime(2024, 10, 1, 11, 0, tzinfo=UTC)  # Event end time

calendar_data = create_calendar_event(
    summary="Team Meeting",
    description="Discussion on project progress",
    location="Conference Room 1",
    start_time=start_time,
    end_time=end_time,
    organizer_email="organizer@example.com"
)

print(calendar_data)

# Write the calendar data to a file
with open('meeting.ics', 'w') as f:
    f.write(calendar_data)
