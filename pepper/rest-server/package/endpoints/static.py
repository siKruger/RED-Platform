import imp
from flask import send_from_directory

from ..server import app

@app.route("/static/<path:path>")
def send_report(path):
    return send_from_directory("static", path)
