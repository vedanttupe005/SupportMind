from flask_sqlalchemy import SQLAlchemy
from config import db
from datetime import datetime
from flask import Flask
from .tickets import Ticket

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    venue = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)

    price = db.Column(db.Numeric(10, 2), nullable=False)

    total_tickets = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    tickets = db.relationship(
        "Ticket",
        back_populates="event",
        cascade="all, delete-orphan"
    )

    payments = db.relationship(
        "Payment",
        back_populates="event",
        cascade="all, delete-orphan"
    )

    def get_remaining_tickets(self):
        booked = Ticket.query.filter_by(event_id=self.id).count()
        return self.total_tickets - booked