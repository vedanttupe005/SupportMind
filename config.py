import os
from flask_sqlalchemy import SQLAlchemy

class Config:
    SECRET_KEY = "vedanttupe005"

    SQLALCHEMY_DATABASE_URI = r"sqlite:///C:\Users\abc\PycharmProjects\Event booking system\instance\event_ticket.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False


db = SQLAlchemy()
