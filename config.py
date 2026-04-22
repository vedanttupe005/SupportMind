import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
load_dotenv()



class Config:
    SECRET_KEY = "vedanttupe005"

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

    SQLALCHEMY_TRACK_MODIFICATIONS = False


db = SQLAlchemy()
