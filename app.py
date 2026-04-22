from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config, db
from models_.event import Event
from ai_controller import ask_ai
from models_.user import User
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from models_.tickets import Ticket
from models_.payment import Payment

import os
load_dotenv()



from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user




app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)


oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template("chat.html")


from flask_login import login_required, current_user
from flask import render_template, abort
from sqlalchemy import func

   # wherever db is initialized


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    # allow only admin
    if current_user.role != "ADMIN":

        abort(403)


    # total users
    total_users = User.query.count()


    # total events
    total_events = Event.query.count()


    # total tickets sold
    total_tickets = Ticket.query.count()


    # total revenue
    total_revenue = db.session.query(

        func.sum(Payment.amount)

    ).scalar() or 0


    # tickets sold per event
    tickets_per_event = (

        db.session.query(

            Event.title,

            func.count(Ticket.id)

        )

        .join(Ticket)

        .group_by(Event.id)

        .all()

    )


    # recent bookings
    recent_bookings = (

        db.session.query(

            User.email,

            Event.title,

            Ticket.id,

            Ticket.status

        )

        .join(Ticket, Ticket.user_id == User.id)

        .join(Event, Event.id == Ticket.event_id)

        .order_by(Ticket.id.desc())

        .limit(5)

        .all()

    )


    return render_template(

        "admin/dashboard.html",

        total_users=total_users,

        total_events=total_events,

        total_tickets=total_tickets,

        total_revenue=total_revenue,

        tickets_per_event=tickets_per_event,

        recent_bookings=recent_bookings

    )


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


@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid username")
            return redirect(url_for('auth.login'))
        if not user.check_password(password):
            flash("Invalid password")
            return redirect(url_for('auth.login'))

        login_user(user)

        return redirect(url_for('home'))


    return render_template("login.html")


@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/ai/googlecallback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()

    except Exception as e:
        print("exception:", e)
        flash("Authorization failed. Please try again.")
        return redirect(url_for('login'))


    user_info = token.get("userinfo")
    if not user_info:
        flash("Unable to fetch Google user info.", "danger")
        return redirect(url_for("login"))


    email = user_info["email"]
    name = user_info["name"]


    user = User.query.filter_by(email=email).first()
    if  user:
        login_user(user)
        return redirect(url_for('home'))

    else:
        user = User(
            name=name,
            email=email,
            auth_provider="GOOGLE"
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)

        return redirect(url_for('home'))



@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("home")
    )

print(os.getenv("DATABASE_URL"))


if __name__ == "__main__":
    app.run(debug=True)