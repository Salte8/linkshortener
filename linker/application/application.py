from flask import render_template
import re
from .account import Account
from .links import Links



class Application:
    def __init__(self):
        self.account = Account()
        self.links = Links()
    
    def home(self):
        return render_template("home.html")
