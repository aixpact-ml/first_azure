import pandas as pd
import logging
import datetime
import requests
import os
import json
import uuid
import mimetypes
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from flask_mail import Message
from werkzeug.utils import secure_filename

# https://medium.com/zenofai/creating-chatbot-using-python-flask-d6947d8ef805
import dialogflow
import pusher

from .forms import FileForm, UploadForm, ChatForm

from config.settings import config
from utils.functions import _log_msg, allowed_file, binary2csv, predict
from utils.email import send_email, mail
from utils.decorators import fire_and_forget

from webapp.extensions import mail
from . import blueprint


def dialogflow_client():
    """TODO"""
    # https://github.com/googleapis/dialogflow-python-client-v2/issues/71
    from google.oauth2.service_account import Credentials

    project_id = os.getenv('APPSETTING_DIALOGFLOW_PROJECT_ID',
                            config.DIALOGFLOW_PROJECT_ID)
    app_creds_json = os.getenv('APPSETTING_GOOGLE_APPLICATION_CREDENTIALS',
                            config.GOOGLE_APPLICATION_CREDENTIALS)

    credentials = Credentials.from_service_account_info(app_creds_json)
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session_id = 'unique'
    session = session_client.session_path(project_id, session_id)
    return session, session_client


def detect_intent_texts(text, language_code):
    """"""
    # https://github.com/googleapis/dialogflow-python-client-v2/issues/71
    # project_id = os.getenv('APPSETTING_DIALOGFLOW_PROJECT_ID',
    #                         config.DIALOGFLOW_PROJECT_ID)
    # app_creds_json = os.getenv('APPSETTING_GOOGLE_APPLICATION_CREDENTIALS',
    #                         config.GOOGLE_APPLICATION_CREDENTIALS)

    # from google.oauth2.service_account import Credentials
    # credentials = Credentials.from_service_account_info(app_creds_json)
    # session_client = dialogflow.SessionsClient(credentials=credentials)

    # session_id = 'unique'
    # # session_client = dialogflow.SessionsClient()
    # session = session_client.session_path(project_id, session_id)


    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)

        query_input = dialogflow.types.QueryInput(text=text_input)

        # create and re-use session
        try:
            response = session_client.detect_intent(
                session=session, query_input=query_input)
        except:
            session, session_client = dialogflow_client()
            response = session_client.detect_intent(
                session=session, query_input=query_input)

        return response.query_result.fulfillment_text


def handle_uploaded_file(file):
    # Azure vs. local, web form vs. POST
    try:
        os.mkdir('./data')
    except:
        pass
    file_temp = f'temp_in.{file.filename.split(".")[-1]}'
    file_dest = os.path.join('./data', file_temp)
    try:
        # When file in is raw data
        with open(file_dest, "wb") as dest:
            dest.write(file)
        print('DEBUG write to file', type(file))
        logging.info('DEBUG write to file', type(file))
    except:
        # When file_in is <class 'werkzeug.datastructures.FileStorage'>
        file.save(file_dest)
        file.close()
        print('DEBUG save as file', type(file))
        logging.info('DEBUG save as file', type(file))
    return file_dest


@blueprint.route('/hello', methods=['GET', 'POST'])
def hello():
    # return jsonify(status='succes', response='webapp is running')
    if request.method == 'POST':
        # https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
        return jsonify(status='succes', response=f'Hello, {request.form.get("name")}!')
    else:
        return render_template('base_empty.html')
        # TODO jsonify(status='succes', response='webapp is running')


@blueprint.route('/debug', methods=['GET', 'POST'])
def debug():
    # POST function
    # url = f'https://hello-aixpact.azurewebsites.net/api/{function}'
    # response = requests.post(url, data={'name': request.args.get('name')})
    # GET function
    url = f'https://hello-aixpact.azurewebsites.net/api/{function}?name={request.args.get("name")}'
    response = requests.get(url)
    return jsonify(status='succes',
                   response=str(response))


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    """HttpTrigger optimised/"""

    form = FileForm()

    # Set csrf token in hidden field - avoid error message
    csrf_token = eval(str(form.csrf_token).split('=')[-1][:-1])
    form.csrf_token.data = csrf_token

    # form.comments.data = form.email.data

    if form.validate_on_submit():
        file = form.file.data
        email = form.email.data
        function = form.function.data
        # form.comments.data = form.email.data

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Predict - HttpTrigger
            try:
                file_dest = handle_uploaded_file(file)
                blob_uri = predict(file_dest, email, function)
            except Exception as err:
                return jsonify(status='failed', error=str(err))
        logging.info('DEBUG log', blob_uri)
        print('DEBUG print', blob_uri)

        return redirect(url_for('base_blueprint.thankyou', name=email.split('@')[0]))

    return render_template('base/upload.html', form=form, func=session.get('populate'))


@blueprint.route("/thankyou")
def thankyou():
    name = request.args.get('name')
    return render_template('base/thank_you.html', name=name)


@blueprint.route("/function/<function_name>")
def function(function_name):
    """Takes some time....."""
    response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
    return response.text


@blueprint.route('/populate/<value>')
def populate(value):

    # TODO get/load instructions from file/dict/env/db
    comments_dict = {'HttpTrigger': 'Forecast instructions here......',
                    'Hello': 'Hello instructions here......',
                    'ForecastAPI': 'Forecast Temperature........'
                    }

    # Store in session
    session['info'] = comments_dict.get(value)
    print(session.get(value), session.get(value))

    return jsonify(comments_dict.get(value))


@blueprint.route('/streamlit/<dash>', methods=['GET', 'POST'])
def streamlit(dash):
    """Route to streamlit port"""

    iframe = f'http://localhost:{dash}8501/'

    form = UploadForm()

    # Set csrf token in hidden field - avoid error message
    csrf_token = eval(str(form.csrf_token).split('=')[-1][:-1])
    form.csrf_token.data = csrf_token

    if form.validate_on_submit():
        file = form.file.data
        session['info'] = 'test this session cookie'
        if file and allowed_file(file.filename):
            try:
                file_dest = os.path.join('./data', file.filename)
                file.save(file_dest)
            except Exception as err:
                return jsonify(status='failed', error=str(err))

        return render_template('base/streamlit.html', form=form, iframe=iframe)

    return render_template('base/streamlit.html', form=form, iframe=iframe)


@blueprint.route('/webhook', methods=['POST'])
def webhook():
    """"""
    try:
        data = request.get_json()
        query_text = data['queryResult']['queryText']
        response = {
            "fulfillmentText": f'Default webhook fullfilment response on query: "{query_text}"'
            }
    except Exception as err:
        return jsonify(status='fail', error=err)

    return jsonify(response)


@blueprint.route('/send_message', methods=['POST'])
def send_message():
    """Form is posted by dialogFlow"""
    message = request.form['message']
    fulfillment_text = detect_intent_texts(message, 'en')
    response_text = {"message": fulfillment_text}
    return jsonify(response_text)


@blueprint.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat runs by custom js script."""

    return render_template('base/dialogue.html')


# @blueprint.route('/chat', methods=['GET', 'POST'])
# def chat():
#     """Route to dialogflow port"""

#     # form = ChatForm()

#     # # Set csrf token in hidden field - avoid error message
#     # csrf_token = eval(str(form.csrf_token).split('=')[-1][:-1])
#     # form.csrf_token.data = csrf_token
#     # message = 'no message'
#     # if form.validate_on_submit():
#     #     message = form.message.data
#     #     flash(message)

#     #     return render_template('base/dialogue.html', form=form)
#     # flash(message)
#     return render_template('base/dialogue.html')
