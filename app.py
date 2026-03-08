from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config, db
from models_.event import Event
from ai_controller import ask_ai




app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)




@app.route("/")
def home():
    return render_template("chat.html")


@app.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    response = ask_ai(user_message)

    return jsonify({
        "response": response
    })

if __name__ == "__main__":
    app.run(debug=True)