from google import genai
import os
from dotenv import load_dotenv
from ai_tools import run_tool
from business_pilicies import BUSINESS_POLICIES

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat_history = []


def ask_ai(user_message):

    # save user message
    chat_history.append({
        "role": "user",
        "content": user_message
    })
    # delete old messages to keep context window manageable only store recent 8 chats
    if len(chat_history) > 8:
        chat_history.pop(0)

    SYSTEM_PROMPT = f"""
    You are an AI support assistant for an event booking website.

    Follow these business policies strictly.

    {BUSINESS_POLICIES}

    Rules:
    1. If a user asks to book tickets, tell them to use the website booking page.
    2. Never say you can book tickets.
    3. Use backend tools only when event or ticket data is required.
    """

    # Gemini tool schema
    tools = [
        {
            "function_declarations": [
                {
                    "name": "get_events",
                    "description": "List all available events"
                },
                {
                    "name": "get_event_details",
                    "description": "Get full details of an event including description, venue, date and price",
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
                    "description": "Check how many tickets are remaining for an event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "event_title": {"type": "string"}
                        },
                        "required": ["event_title"]
                    }
                }
            ]
        }
    ]

    # build conversation context
    conversation = SYSTEM_PROMPT + "\n"

    for msg in chat_history:
        conversation += f"{msg['role']}: {msg['content']}\n"



    # ask Gemini
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=[
            {"role": "user", "parts": [{"text": conversation}]}
        ],
        config={
            "tools": tools
        }
    )

    part = response.candidates[0].content.parts[0]

    # -------- TOOL CALL --------
    if hasattr(part, "function_call")and part.function_call:

        tool_call = part.function_call

        tool_name = tool_call.name
        args = dict(tool_call.args)

        result = run_tool(tool_name, args)

        # send tool result back to Gemini for explanation
        final_response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=f"""
            Conversation so far:
            {conversation}

            Tool result:
            {result}

            Using the tool result, answer the user's latest question.
            """
        )

        reply = final_response.text

    else:
        reply = response.text

    # save assistant reply
    chat_history.append({
        "role": "assistant",
        "content": reply
    })

    return reply