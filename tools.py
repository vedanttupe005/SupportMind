from models_.event import Event
from models_.tickets import Ticket
from models_.payment import Payment  # make sure this exists
from flask_login import current_user
from sqlalchemy import func

from functools import lru_cache


# -----------------------------------
# 🔹 HELPER: SAFE EVENT FETCH
# -----------------------------------
def find_event(event_title):
    return Event.query.filter(
        Event.title.ilike(f"%{event_title.strip()}%")
    ).first()


# -----------------------------------
# 🔹 GET ALL EVENTS (CACHED)
# -----------------------------------
@lru_cache(maxsize=50)
def get_events():

    events = Event.query.all()

    return [
        {
            "title": e.title,
            "description": e.description,
            "venue": e.venue,
            "event_date": str(e.event_date),
            "price": float(e.price)
        }
        for e in events
    ]


# -----------------------------------
# 🔹 EVENT DETAILS (IMPROVED)
# -----------------------------------
def get_event_details(event_title):

    event = find_event(event_title)

    if not event:
        return {
            "error": "Event not found",
            "message": "Try checking event name or view all events."
        }

    return {
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "event_date": str(event.event_date),
        "price": float(event.price),
        "remaining_tickets": event.get_remaining_tickets()
    }


# -----------------------------------
# 🔹 EVENT PRICE
# -----------------------------------
def get_event_price(event_title):

    event = find_event(event_title)

    if not event:
        return {
            "error": "Event not found",
            "message": "Try checking event name."
        }

    return {
        "title": event.title,
        "price": float(event.price)
    }


# -----------------------------------
# 🔹 TICKETS SOLD
# -----------------------------------
def tickets_sold(event_title):

    event = find_event(event_title)

    if not event:
        return {"error": "Event not found"}

    sold = Ticket.query.filter_by(event_id=event.id).count()

    return {
        "event": event.title,
        "tickets_sold": sold
    }


# -----------------------------------
# 🔹 TICKETS LEFT
# -----------------------------------
def tickets_left(event_title):

    event = find_event(event_title)

    if not event:
        return {"error": "Event not found"}

    remaining = event.get_remaining_tickets()

    return {
        "event": event.title,
        "tickets_left": remaining
    }


# -----------------------------------
# 🔹 USER TICKETS
# -----------------------------------
def get_user_tickets():

    if not current_user.is_authenticated:
        return {
            "error": "AUTH_REQUIRED",
            "message": "Please login to view your booked tickets."
        }

    tickets = (
        Ticket.query
        .join(Event)
        .filter(Ticket.user_id == current_user.id)
        .all()
    )

    if not tickets:
        return {"message": "You have no booked tickets."}

    return [
        {
            "event": t.event.title,
            "date": str(t.event.event_date),
            "ticket_id": t.id,
            "status": t.status
        }
        for t in tickets
    ]



# ============================================================
# 🔥 ADMIN TOOLS (NO db.session, NO circular import)
# ============================================================

# -----------------------------------
# 🔹 TOTAL REVENUE
# -----------------------------------
def get_total_revenue():

    payments = Payment.query.filter_by(status="PENDING").all()

    total = sum(float(p.amount) for p in payments)

    return {
        "total_revenue": total
    }


# -----------------------------------
# 🔹 MOST POPULAR EVENT
# -----------------------------------
def most_popular_event():

    events = Event.query.all()

    best_event = None
    max_tickets = 0

    for e in events:
        count = Ticket.query.filter_by(event_id=e.id).count()

        if count > max_tickets:
            max_tickets = count
            best_event = e

    if not best_event:
        return {"message": "No data available"}

    return {
        "event": best_event.title,
        "tickets_sold": max_tickets
    }


# -----------------------------------
# 🔹 TICKETS PER EVENT
# -----------------------------------
def tickets_per_event():

    events = Event.query.all()

    result = []

    for e in events:
        count = Ticket.query.filter_by(event_id=e.id).count()

        result.append({
            "event": e.title,
            "tickets_sold": count
        })

    return result


# -----------------------------------
# 🔹 RECENT BOOKINGS
# -----------------------------------
def recent_bookings(limit=5):

    tickets = (
        Ticket.query
        .join(Event)
        .order_by(Ticket.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "event": t.event.title,
            "user_id": t.user_id,
            "ticket_id": t.id,
            "status": t.status
        }
        for t in tickets
    ]