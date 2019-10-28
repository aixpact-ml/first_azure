import requests
import json
from flask import Flask
from flask import (Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response)

app = Flask(__name__)


@app.route("/")
def index():
    """"""
    r = requests.get('http://www.aixpact.ml/api/httptrigger?name=frank')
    # print(r.content, r.status_code)

    return r.text #, jsonify({'name':r.text})
