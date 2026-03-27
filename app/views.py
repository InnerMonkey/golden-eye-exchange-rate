from flask import request
from app import app
import controllers


@app.route("/")
def hello():
    return "Hello everybody!"

@app.route("/xrates")
def view_rates():
    return controllers.ViewAllRates().call()

@app.route("/api/xrates/<fmt>")
def api_rates(fmt):
    return controllers.ViewAllRates().call(fmt)