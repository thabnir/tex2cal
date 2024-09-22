## Inspiration
The inspiration for this project came during a chaotic pre-hackathon week, when two of us missed an important assignment deadline. Despite having taken pictures of the syllabus on a whiteboard, we simply forgot to transfer the dates to our calendars manually. We realized that we weren't alone in this – many people take pictures of posters, whiteboards, and syllabi, but never get around to manually adding each event or deadline to their calendar. This sparked the idea: what if we could automate the process of turning images, text, and even speech into a calendar that’s ready to use?

## What it does
Our project automatically generates calendar events from various types of input. Whether you upload a photo of a poster, screenshot a syllabus, or take a picture of a whiteboard, the system parses the image and converts the text into a .ical file that can be imported into any calendar app. You can also type your input directly or (soon) speak to the system to request a schedule, itinerary, or event. 

Need to create a workout routine? Ask it. Planning a day of tourism? It can build a personalized itinerary. It’s a tool designed to save you time by turning your notes, images, and thoughts into structured calendar events instantly.

## How we built it
We developed a Flask-based web frontend that allows users to upload an image, take a picture with their webcam, or directly type to the system. For speech input, we use Google's speech-to-text API. The image processing and text parsing are powered by GPT-4o vision capabilities through an API, which converts the recognized text into a structured .ical format using GPT4o’s natural language processing and function-calling capabilities. The .ical files can be instantly imported into any calendar app.

## Challenges we ran into
One major challenge was dealing with large base64-encoded images. Sometimes the image requests would break due to size limits when transmitted to the vision API. It took some fine-tuning to optimize the way we handle image uploads and improve reliability. Additionally, it took time to get GPT4o’s function calling and text-to-calendar processing working consistently, especially when handling diverse inputs like itineraries, academic deadlines, and personal schedules.

## Accomplishments that we're proud of
We’re proud of how intuitive and versatile the system turned out to be. It successfully parses input from images, speech, and text, creating usable .ical files. It can handle a wide variety of use cases, from converting a physical agenda into a digital calendar, to building custom itineraries for travel or fitness. Seeing this system make sense of such diverse data inputs is a real win for us.

## What we learned
We learned a great deal about handling different forms of input—especially speech and images—and converting them into structured data that people can use in a practical way. Optimizing requests and ensuring the system could handle large inputs efficiently taught us valuable lessons about image processing and API limitations. Additionally, working with function-calling in GPT4o showed us how to dynamically convert parsed text into meaningful data.

## What's next for TBD
Next up, we plan to complete the integration of speech input, allowing users to talk to the system for hands-free scheduling. We also want to extend the platform’s capabilities by adding support for recurring events, better handling of multi-page documents like syllabi, and the ability to sync directly with calendar apps in real-time. We see endless possibilities for expanding the way users can interact with their schedules, making the entire process even more seamless and automatic.
