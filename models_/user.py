from flask_sqlalchemy import SQLAlchemy
from config import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash




class User(UserMixin,db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=True)

    auth_provider = db.Column(db.String(20), nullable=False, default="LOCAL")
    role = db.Column(db.String(20), nullable=False, default="USER")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    tickets = db.relationship(
        "Ticket",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    payments = db.relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)