from os import environ
from flaskext.mysql import MySQL
from app import app


mysql = MySQL(app)

# MySQL configurations
app.config["MYSQL_DATABASE_USER"] = environ.get("DATABASE_USER")
app.config["MYSQL_DATABASE_PASSWORD"] = environ.get("DATABASE_PASSWORD")
app.config["MYSQL_DATABASE_DB"] = environ.get("DATABASE_DB")
app.config["MYSQL_DATABASE_HOST"] = environ.get("DATABASE_HOST")

db_connection = mysql.connect()


def get_cursor():
    db_connection.ping()
    return db_connection.cursor()
