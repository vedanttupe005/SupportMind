from flask_sqlalchemy import SQLAlchemy
from config import db
from datetime import datetime
import uuid



class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)

    ticket_uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="UNUSED"
    )

    payment_id = db.Column(
        db.Integer,
        db.ForeignKey("payments.id", name='fk_tickets_payment_id'),
        nullable=False
    )

    used_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    #relationships
    user = db.relationship("User", back_populates="tickets")
    event = db.relationship("Event", back_populates="tickets")
    payment = db.relationship("Payment", back_populates="tickets")

