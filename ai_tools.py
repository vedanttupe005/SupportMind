from tools import *
from flask_login import current_user

# -----------------------------------
# 🔐 ADMIN TOOL LIST
# -----------------------------------
ADMIN_TOOLS = {
    "get_total_revenue",
    "tickets_per_event",
    "recent_bookings"
}


# -----------------------------------
# 🛠 TOOL RUNNER (SECURE)
# -----------------------------------
def run_tool(tool_name, args=None):

    if args is None:
        args = {}

    print(f"\n🛠 TOOL REQUEST: {tool_name} | ARGS: {args}")

    # -----------------------------------
    # 🔐 ADMIN ACCESS CONTROL
    # -----------------------------------
    if tool_name in ADMIN_TOOLS:

        if not current_user.is_authenticated:
            print("❌ NOT LOGGED IN")
            return {
                "error": "AUTH_REQUIRED",
                "message": "Please login to access this information."
            }

        if current_user.role != "ADMIN":
            print(f"❌ ACCESS DENIED | USER ROLE: {current_user.role}")
            return {
                "error": "UNAUTHORIZED",
                "message": "This information is restricted to admin users only."
            }

        print("✅ ADMIN ACCESS GRANTED")

    # -----------------------------------
    # 👤 USER TOOLS
    # -----------------------------------
    if tool_name == "get_events":
        return get_events()

    elif tool_name == "get_event_details":
        return get_event_details(args.get("event_title"))

    elif tool_name == "get_event_price":
        return get_event_price(args.get("event_title"))

    elif tool_name == "tickets_sold":
        return tickets_sold(args.get("event_title"))

    elif tool_name == "tickets_left":
        return tickets_left(args.get("event_title"))

    elif tool_name == "get_user_tickets":
        return get_user_tickets()


    # -----------------------------------
    # 🔥 ADMIN TOOLS
    # -----------------------------------
    elif tool_name == "get_total_revenue":
        return get_total_revenue()

    elif tool_name == "most_popular_event":
        return most_popular_event()

    elif tool_name == "tickets_per_event":
        return tickets_per_event()

    elif tool_name == "recent_bookings":
        return recent_bookings()


    # -----------------------------------
    # ❌ UNKNOWN TOOL
    # -----------------------------------
    print("❌ UNKNOWN TOOL CALLED")
    return {"error": "Unknown tool"}