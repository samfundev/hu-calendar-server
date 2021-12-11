import flask
from flask import request, redirect, url_for, render_template
from flask.blueprints import Blueprint
import flask_login
from flask_login.utils import login_required
from app import app
from db_config import get_cursor, db_connection

login_manager = flask_login.LoginManager(app)
login_blueprint = Blueprint("login", __name__)


class User(flask_login.UserMixin):
    def __init__(self, user_id) -> None:
        super().__init__()
        self.id = user_id


@login_manager.user_loader
def user_loader(user_id):
    cursor = get_cursor()
    cursor.execute("SELECT ID FROM `Users` WHERE ID=%s", user_id)
    row = cursor.fetchone()
    if row is None:
        return None

    return User(user_id)


@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")

    first = flask.request.form["first"]
    last = flask.request.form["last"]
    password = flask.request.form["password"]

    # I understand that it a sin to store passwords in plaintext.
    # I understand that it is a sin to not sanitize SQL parameters.
    cursor = get_cursor()
    cursor.execute(
        "SELECT ID FROM `Users` WHERE FirstName=%s and LastName=%s and Password=%s",
        (first, last, password),
    )
    row = cursor.fetchone()
    if row is None:
        return flask.redirect(flask.url_for(".login"))

    user = User(str(row[0]))
    flask_login.login_user(user)
    return flask.redirect(flask.url_for("index"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    first = request.form["first"]
    last = request.form["last"]
    password = request.form["password"]

    cursor = get_cursor()
    cursor.execute(
        "INSERT INTO `Users` (FirstName, LastName, Password) VALUES (%s, %s, %s)",
        (first, last, password),
    )

    db_connection.commit()

    user = User(str(cursor.lastrowid))
    flask_login.login_user(user)
    return redirect(url_for(".index"))


@app.route("/signout", methods=["GET"])
@login_required
def signout():
    flask_login.logout_user()
    return redirect(url_for(".index"))
