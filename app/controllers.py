from flask import render_template

from models import XRate

def get_all_rates():
    xrates = XRate.select()
    return render_template("xrates.html", xrates=xrates)