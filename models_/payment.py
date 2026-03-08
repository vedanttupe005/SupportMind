from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from config import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

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

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    currency = db.Column(
        db.String(10),
        nullable=False,
        default="INR"
    )

    provider = db.Column(
        db.String(20),
        nullable=False
    )  # RAZORPAY / STRIPE

    provider_payment_id = db.Column(
        db.String(255),
        unique=True,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING"
    )  # PENDING / SUCCESS / FAILED

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )



    # relationships
    user = db.relationship("User", back_populates="payments")

    event = db.relationship("Event", back_populates="payments")

    tickets = db.relationship(
        "Ticket",
        back_populates="payment",
        cascade="all, delete-orphan"
    )