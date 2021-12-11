from os import environ
from datetime import date
from flask import Flask
from flask.json import JSONEncoder

# https://stackoverflow.com/a/43663918
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


app = Flask(__name__)
app.secret_key = environ.get("SECRET_KEY")
app.json_encoder = CustomJSONEncoder
