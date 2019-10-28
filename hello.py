import requests
from flask import Flask
from flask import (Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response)

app = Flask(__name__)


@app.route("/")
def index():
    """"""
    api_ = requests.get'http://www.aixpact.ml/api/httptrigger?name=frank')
    return f"<h1>Hello {api_}!</h1>"
