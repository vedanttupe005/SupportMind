from models_.event import Event
from models_.tickets import Ticket


def get_events():

    events = Event.query.all()

    result = []

    for e in events:
        result.append({
            "title": e.title,
            "description": e.description,
            "venue": e.venue,
            "event_date": str(e.event_date),
            "price": float(e.price)
        })

    return result


def get_event_details(event_title):

    event = Event.query.filter(
        Event.title.ilike(f"%{event_title}%")
    ).first()

    if not event:
        return {"error": "Event not found"}

    return {
        "title": event.title,
        "description": event.description,
        "venue": event.venue,
        "event_date": str(event.event_date),
        "price": float(event.price)
    }


def get_event_price(event_title):

    event = Event.query.filter(
        Event.title.ilike(f"%{event_title}%")
    ).first()

    if not event:
        return {"error": "Event not found"}

    return {
        "title": event.title,
        "price": float(event.price)
    }


def tickets_sold(event_title):

    event = Event.query.filter(
        Event.title.ilike(f"%{event_title}%")
    ).first()

    if not event:
        return {"error": "Event not found"}

    sold = Ticket.query.filter_by(event_id=event.id).count()

    return {
        "event": event.title,
        "tickets_sold": sold
    }


def tickets_left(event_title):

    event = Event.query.filter(
        Event.title.ilike(f"%{event_title}%")
    ).first()

    if not event:
        return {"error": "Event not found"}

    remaining = event.get_remaining_tickets()

    return {
        "event": event.title,
        "tickets_left": remaining
    }