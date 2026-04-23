from google import genai
import os
import time
import random
from dotenv import load_dotenv
from ai_tools import run_tool
from business_pilicies import BUSINESS_POLICIES

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chat_history = []

PRIMARY_MODEL = "gemini-3.1-flash-lite-preview"
FALLBACK_MODEL = "gemini-2.5-flash-lite"


# -----------------------------
# 🔁 SAFE GEMINI CALL (Retry)
# -----------------------------
def safe_gemini_call(**kwargs):
    for attempt in range(3):
        try:
            return client.models.generate_content(**kwargs)

        except Exception as e:
            if "503" in str(e):
                wait = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying Gemini... attempt {attempt+1}")
                time.sleep(wait)
            else:
                raise e

    raise Exception("Gemini failed after retries")


# -----------------------------
# 🤖 MAIN AI FUNCTION
# -----------------------------
def ask_ai(user_message):
    models = client.models.list()

    for m in models:
        print(m.name)

    try:
        msg = user_message.lower()

        # -----------------------------
        # ⚡ RULE-BASED SHORTCUTS (Reduce AI calls)
        # -----------------------------
        if "all events" in msg or "what events" in msg:
            return run_tool("get_events", {})

        # You can expand this later with NLP/regex

        # -----------------------------
        # 💾 SAVE USER MESSAGE
        # -----------------------------
        chat_history.append({
            "role": "user",
            "content": user_message
        })

        # keep only last 8 messages
        if len(chat_history) > 8:
            chat_history[:] = chat_history[-8:]

        # -----------------------------
        # 🧠 SYSTEM PROMPT
        # -----------------------------
        SYSTEM_PROMPT = f"""
You are an AI support assistant for an event booking website.
Link: https://event-booking-iif4.onrender.com/

Follow these business policies strictly:

{BUSINESS_POLICIES}

Rules:
1. If a user asks to book tickets, tell them to use the website booking page.
2. Never say you can book tickets.
3. Use backend tools only when event or ticket data is required.
"""

        # -----------------------------
        # 🔧 TOOL DEFINITIONS
        # -----------------------------
        tools = [
            {
                "function_declarations": [
                    {
                        "name": "get_events",
                        "description": "Get all available events"
                    },
                    {
                        "name": "get_event_details",
                        "description": "Get full details of an event",
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
                        "description": "Check remaining tickets",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "event_title": {"type": "string"}
                            },
                            "required": ["event_title"]
                        }
                    },
                    {
                        "name": "get_user_tickets",
                        "description": "Get tickets booked by user",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        ]

        # -----------------------------
        # 🧾 BUILD CONVERSATION
        # -----------------------------
        conversation = SYSTEM_PROMPT + "\nRecent conversation:\n"

        for msg_item in chat_history:
            conversation += f"{msg_item['role']}: {msg_item['content']}\n"

        # -----------------------------
        # 🤖 FIRST GEMINI CALL
        # -----------------------------
        response = safe_gemini_call(
            model=PRIMARY_MODEL,
            contents=[{
                "role": "user",
                "parts": [{"text": conversation}]
            }],
            config={"tools": tools}
        )

        # -----------------------------
        # 🛡 SAFE PARSE
        # -----------------------------
        try:
            part = response.candidates[0].content.parts[0]
        except (IndexError, AttributeError):
            return "⚠️ AI could not generate a response. Please try again."

        # -----------------------------
        # 🔧 TOOL CALL HANDLING
        # -----------------------------
        if hasattr(part, "function_call") and part.function_call:

            tool_call = part.function_call
            tool_name = tool_call.name
            args = dict(tool_call.args)

            result = run_tool(tool_name, args)

            # -----------------------------
            # 🤖 SECOND GEMINI CALL (Explain result)
            # -----------------------------
            final_response = safe_gemini_call(
                model=FALLBACK_MODEL,
                contents=f"""
Conversation:
{conversation}

Tool result:
{result}

Answer the user's latest question using this data.
"""
            )

            reply = getattr(final_response, "text", None) or "⚠️ Unable to process response."

        else:
            reply = getattr(response, "text", None) or "⚠️ No response generated."

        # -----------------------------
        # 💾 SAVE AI RESPONSE
        # -----------------------------
        chat_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    # -----------------------------
    # ❌ GLOBAL ERROR HANDLER
    # -----------------------------
    except Exception as e:
        print("AI ERROR:", str(e))
        return "⚠️ AI is busy right now. Please try again."