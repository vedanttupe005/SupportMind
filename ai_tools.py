from tools import *

def run_tool(tool_name, args=None):

    if args is None:
        args = {}

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

    else:
        return {"error": "Unknown tool"}

