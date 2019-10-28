import requests
from flask import Flask
from flask import (Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response)

app = Flask(__name__)


@app.route("/")
def index():
    """"""
    r = requests.get('http://www.aixpact.ml/api/httptrigger?name=frank')
    text = json.loads(r.text)
    return jsonify(r) #f"<h1>Hello {api_}!</h1>"
