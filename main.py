from flask import request, current_app, render_template, redirect, url_for
from flask.json import jsonify
from flask_login import current_user, login_required
from app import app
from db_config import get_cursor, db_connection
from login import login_blueprint


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    date = request.args.get("date", "").strip()
    location = request.args.get("location", "").strip()

    cursor = get_cursor()

    query = "SELECT * FROM `Events`"
    if date != "" or location != "":
        filters = []
        if date != "":
            filters.append("DATE(Date) = %(date)s")

        if location != "":
            filters.append("Location = %(location)s")

        query += " WHERE " + " and ".join(filters)

    cursor.execute(query, {"date": date, "location": location})
    results = list(cursor.fetchall())

    attending = []
    if current_user.is_authenticated:
        cursor.execute(
            "SELECT EventID FROM `Attendees` WHERE UserID=%s", current_user.id
        )

        attending = [a[0] for a in cursor.fetchall()]

    for i in range(len(results)):
        result = results[i]
        attending_status = result[0] in attending
        if current_user.is_authenticated and str(result[4]) == current_user.id:
            attending_status = None

        results[i] = result + (attending_status,)

    return render_template("search.html", results=results)


@app.route("/calendar")
@login_required
def calendar():
    return render_template("calendar.html")


@app.route("/create")
@login_required
def create():
    return render_template("create.html")


@app.route("/create_event", methods=["POST"])
@login_required
def create_event():
    title = request.form["title"]
    date = request.form["date"]
    location = request.form["location"]
    description = request.form["description"]

    cursor = get_cursor()
    cursor.execute(
        "INSERT INTO `Events` (Title, Date, Location, Description, OwnerID) VALUES (%s, %s, %s, %s, %s)",
        (title, date, location, description, current_user.id),
    )

    db_connection.commit()

    return redirect(url_for(".calendar"))


@app.route("/join_event", methods=["POST"])
@login_required
def join_event():
    event_id = request.form["event_id"]

    cursor = get_cursor()

    cursor.execute("SELECT * FROM `Events` WHERE ID=%s", event_id)
    if cursor.fetchone() is None:
        return jsonify(False)

    cursor.execute(
        "INSERT INTO `Attendees` (EventID, UserID) VALUES (%s, %s)",
        (event_id, current_user.id),
    )

    db_connection.commit()

    return jsonify(True)


@app.route("/leave_event", methods=["POST"])
@login_required
def leave_event():
    event_id = request.form["event_id"]

    cursor = get_cursor()

    cursor.execute("SELECT * FROM `Events` WHERE ID=%s", event_id)
    if cursor.fetchone() is None:
        return jsonify(False)

    cursor.execute(
        "DELETE FROM `Attendees` WHERE EventID=%s and UserID=%s",
        (event_id, current_user.id),
    )

    db_connection.commit()

    return jsonify(True)


@app.route("/delete_event", methods=["POST"])
def delete_event():
    event_id = request.form["event_id"]

    cursor = get_cursor()

    cursor.execute("SELECT OwnerID FROM `Events` WHERE ID=%s", event_id)
    row = cursor.fetchone()
    if row is None:
        return jsonify(False)

    if str(row[0]) != current_user.id:
        return current_app.login_manager.unauthorized()

    cursor.execute("DELETE FROM `Attendees` WHERE EventID=%s", (event_id))
    cursor.execute("DELETE FROM `Events` WHERE ID=%s", (event_id))

    db_connection.commit()

    return jsonify(True)


@app.route("/events")
@login_required
def events():
    cursor = get_cursor()
    cursor.execute(
        """SELECT DISTINCT Events.ID, Events.Title, Events.Location, Events.Date, Users.FirstName, Users.LastName, Events.Description FROM `Events`
        LEFT JOIN `Attendees` ON Events.ID = Attendees.EventID
        LEFT JOIN `Users` ON Events.OwnerID = Users.ID
        WHERE Attendees.UserID=%(user)s or Events.OwnerID=%(user)s""",
        {"user": current_user.id},
    )

    return jsonify(cursor.fetchall())


app.debug = True
app.register_blueprint(login_blueprint)

if __name__ == "__main__":
    app.run()
