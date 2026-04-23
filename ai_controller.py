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
# 🤖 MAIN AI FUNCTION (FIXED)
# -----------------------------
def ask_ai(user_message):
    try:
        msg = user_message.lower()

        # -----------------------------
        # ⚡ RULE-BASED SHORTCUTS
        # -----------------------------
        if "all events" in msg or "what events" in msg:
            return run_tool("get_events", {})

        # -----------------------------
        # 💾 SAVE USER MESSAGE
        # -----------------------------
        chat_history.append({
            "role": "user",
            "content": user_message
        })

        if len(chat_history) > 8:
            chat_history[:] = chat_history[-8:]

        # -----------------------------
        # 🧠 STRONG SYSTEM PROMPT
        # -----------------------------
        SYSTEM_PROMPT = f"""
        You are an AI support assistant for an event booking website. link = https://event-booking-iif4.onrender.com/

        STRICT RULES:
        1. ALWAYS call a tool when user asks about:
           - tickets left
           - availability
           - event details
           - price
           - bookings
        2. NEVER guess or assume data
        3. NEVER say "I don't have data"
        4. DO NOT answer from memory
        5. If data is needed → MUST call tool

        IMPORTANT:
        - Some data is admin-only (revenue, analytics, users)
        - If user is not admin, do NOT attempt to access admin data

        {BUSINESS_POLICIES}
        """

        # -----------------------------
        # 🔧 TOOL DEFINITIONS (IMPROVED)
        # -----------------------------
        tools = [
            {
                "function_declarations": [

                    # -----------------------------
                    # 👤 USER TOOLS
                    # -----------------------------
                    {
                        "name": "get_events",
                        "description": "Get list of all available events"
                    },
                    {
                        "name": "get_event_details",
                        "description": "Get full details of a specific event",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "event_title": {
                                    "type": "string",
                                    "description": "Name of the event"
                                }
                            },
                            "required": ["event_title"]
                        }
                    },
                    {
                        "name": "tickets_left",
                        "description": "Get how many tickets are remaining for an event",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "event_title": {
                                    "type": "string",
                                    "description": "Event name"
                                }
                            },
                            "required": ["event_title"]
                        }
                    },
                    {
                        "name": "get_user_tickets",
                        "description": "Get tickets booked by the logged-in user",
                        "parameters": {
                            "type": "object",
                            "properties": {}
                        }
                    },

                    # -----------------------------
                    # 🔥 ADMIN TOOLS
                    # -----------------------------
                    {
                        "name": "get_total_revenue",
                        "description": "Get total revenue from all ticket sales (admin only)"
                    },
                    {
                        "name": "most_popular_event",
                        "description": "Get the event with highest ticket sales (admin only)"
                    },
                    {
                        "name": "tickets_per_event",
                        "description": "Get number of tickets sold for each event (admin only)"
                    },
                    {
                        "name": "recent_bookings",
                        "description": "Get list of recent ticket bookings (admin only)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "description": "Number of recent bookings to return"
                                }
                            }
                        }
                    },

                    # -----------------------------
                    # 📅 DATE-BASED TOOL
                    # -----------------------------
                    {
                        "name": "get_events_by_date",
                        "description": "Get events happening on a specific date",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date": {
                                    "type": "string",
                                    "description": "Date in YYYY-MM-DD format"
                                }
                            },
                            "required": ["date"]
                        }
                    }

                ]
            }
        ]

        # -----------------------------
        # 🧾 STRUCTURED CONVERSATION (FIXED)
        # -----------------------------
        contents = []

        # system prompt
        contents.append({
            "role": "user",
            "parts": [{"text": SYSTEM_PROMPT}]
        })

        # chat history
        for msg_item in chat_history:
            contents.append({
                "role": msg_item["role"],
                "parts": [{"text": msg_item["content"]}]
            })

        # -----------------------------
        # 🤖 FIRST GEMINI CALL
        # -----------------------------
        response = safe_gemini_call(
            model=PRIMARY_MODEL,
            contents=contents,
            config={"tools": tools}
        )

        # -----------------------------
        # 🔍 SAFE FUNCTION CALL PARSING (FIXED)
        # -----------------------------
        try:
            parts = response.candidates[0].content.parts
        except (IndexError, AttributeError):
            return "⚠️ AI failed to respond."

        tool_call = None

        for p in parts:
            if hasattr(p, "function_call") and p.function_call:
                tool_call = p.function_call
                break

        # -----------------------------
        # 🔧 TOOL EXECUTION
        # -----------------------------
        if tool_call:
            tool_name = tool_call.name
            args = dict(tool_call.args)

            print("🔧 TOOL CALLED:", tool_name, args)


            result = run_tool(tool_name, args)

            print("📦 TOOL RESULT:", result)

            # -----------------------------
            # 🚫 HANDLE UNAUTHORIZED DIRECTLY
            # -----------------------------
            if isinstance(result, dict) and result.get("error") in ["UNAUTHORIZED", "AUTH_REQUIRED"]:
                print("🔒 ACCESS BLOCKED:", result)
                return result["message"]

            if isinstance(result, dict) and result.get("error") == "AUTH_REQUIRED":
                return result["message"]

            if result is None:
                return "⚠️ Failed to fetch data."

            # -----------------------------
            # 🤖 SECOND GEMINI CALL (FIXED)
            # -----------------------------
            final_response = safe_gemini_call(
                model=PRIMARY_MODEL,
                contents=[{
                    "role": "user",
                    "parts": [{
                        "text": f"""
User question: {user_message}

Tool result:
{result}

Generate a helpful natural response using this data.
"""
                    }]
                }]
            )

            reply = getattr(final_response, "text", None) or "⚠️ Error generating response."

        else:
            # no tool used
            reply = getattr(response, "text", None) or "⚠️ No response generated."

        # -----------------------------
        # 💾 SAVE RESPONSE
        # -----------------------------
        chat_history.append({
            "role": "assistant",
            "content": reply
        })

        return reply

    except Exception as e:
        print("AI ERROR:", str(e))
        return "⚠️ AI is busy. Try again."