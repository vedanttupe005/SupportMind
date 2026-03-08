from google import genai
import os
from dotenv import load_dotenv
from ai_tools import run_tool

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat_history = []
def ask_ai(user_message):

    chat_history.append({
        "role": "user",
        "content": user_message
    })

    system_prompt = """
You are an AI customer support assistant for an event booking website.

You help users with:
- events
- ticket prices
- event details
- ticket availability
"""

    tools = [
        {
            "name": "get_events",
            "description": "List all available events"
        },
        {
            "name": "get_event_details",
            "description": "Get details of an event",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_title": {"type": "string"}
                },
                "required": ["event_title"]
            }
        },
        {
            "name": "get_event_price",
            "description": "Get price of an event ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_title": {"type": "string"}
                },
                "required": ["event_title"]
            }
        },
        {
            "name": "tickets_left",
            "description": "Check how many tickets remain for an event",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_title": {"type": "string"}
                },
                "required": ["event_title"]
            }
        }
    ]

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        tools=tools
    )

    # check if Gemini called a tool
    if response.candidates[0].content.parts[0].function_call:

        tool_call = response.candidates[0].content.parts[0].function_call

        tool_name = tool_call.name
        args = dict(tool_call.args)

        result = run_tool(tool_name, args)

        # send tool result back to Gemini
        final_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
User question: {user_message}

Tool result:
{result}

Write a helpful answer for the user.
"""
        )

        reply = final_response.text

    else:
        reply = response.text

    chat_history.append({
        "role": "assistant",
        "content": reply
    })

    return reply