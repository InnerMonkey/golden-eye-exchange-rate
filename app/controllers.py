from flask import render_template, make_response

from models import XRate

class BaseController:
    def __init__(self):
        pass

    def call(self, *args, **kwds):
        try:
            return self._call(*args, **kwds)
        except Exception as ex:
            return make_response(str(ex), 500)
    
    def _call(self, *args, **kwds):
        raise NotImplementedError("_call")
    
class ViewAllRates(BaseController):
    def _call(self):
        xrates = XRate.select()
        return render_template("xrates.html", xrates=xrates)


# def get_all_rates():
#     try:    
#         xrates = XRate.select()
#         return render_template("xrates.html", xrates=xrates)
#     except Exception as ex:
#         return make_response(str(ex), 500)