import logging
import datetime
import requests
import os
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from werkzeug.utils import secure_filename
from forms import LoginForm, FileForm

import algo

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from flask_wtf.csrf import CsrfProtect
CsrfProtect(app)

HTTP_BAD_REQUEST = 400
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
SHARED = 'https://helloaixpact.file.core.windows.net/'
LOCAL_PATH = '/home/jovyan/aixpact/project/'
app.config['SHARED'] = SHARED
app.config['LOCAL_PATH'] = LOCAL_PATH
app.config['DEV'] = False


def _log_msg(msg):
    logging.info("{}: {}".format(datetime.datetime.now(), msg))


def allowed_file(filename):
    _log_msg('checking allowed file ...')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

try:
    # https://docs.microsoft.com/en-us/azure/storage/files/storage-python-how-to-use-file-storage
    from azure.storage.file import FileService, ContentSettings
    from azure.storage.blob import BlockBlobService

    storageAccount = 'helloaixpact'
    accountKey = '/K/UXeclbEGQ6qxVEEXLrD47hwrxHGJGJnpGPVNZXu2dEEhJWSJ9G4+iDsvWDx4IfDYpIBW9OM+EX/4iNFbR1g=='
    directory_name = 'sampledir'
    file_in = f'https://helloaixpact.file.core.windows.net/myshare/myfile2'

    file_service = FileService(account_name=storageAccount, account_key=accountKey)
    file_service.create_share('myshare')
    file_service.create_directory('myshare', 'sampledir')

    # Create the BlockBlockService that the system uses to call the Blob service for the storage account.
    # https://docs.microsoft.com/nl-nl/azure/storage/blobs/storage-quickstart-blobs-python
    block_blob_service = BlockBlobService(
        account_name=storageAccount, account_key=accountKey)

    # Create a container called 'quickstartblobs'.
    container_name = 'quickstartblobs'
    block_blob_service.create_container(container_name)

    # Set the permission so the blobs are public.
    # block_blob_service.set_container_acl(
    #     container_name, public_access=PublicAccess.Container)
except:
    print('local debug')


def to_blob(file, container_name='quickstartblobs', blob_name='myblob', app_name='helloaixpact'):
    """"""
    # Save file to root dir in Azure - create path
    file_name = file.filename
    file.save(file_name)

    # Upload the file from path
    block_blob_service.create_blob_from_path(container_name, blob_name, file_name)
    http = f'https://{app_name}.blob.core.windows.net/{container_name}/{blob_name}'
    logging.info(f'Blob upload finished @ {http}')
    return http


@app.route("/hello", methods=['GET', 'POST'])
def hello():
    """Test"""
    try:
        name = request.args.get('name')
    except:
        name = 'stranger'
    return jsonify(status='succes', response=f'hello {name}')


@app.route("/hello/<name>")
def hello2(name):
    """Test"""
    # try:
    #     name = request.args.get('name')
    # except:
    #     name = 'stranger'
    return jsonify(status='succes', response=f'hello {name}')


@app.route("/")
def index():
    """Takes some time....."""
    text = 'woh'
    logging.info(f'some logging {text}')
    # r = requests.get('http://www.aixpact.ml/api/httptrigger?name=frank')
    # print(r.content, r.status_code)
    return jsonify(status='succes', response='api is online') #r.text


@app.route("/files")
def files():
    """"""
    # if the file in the root path of the share, please let the directory name as ''
    # file = file_service.get_file_to_text(share_name, directory_name, file_name)
    # print(file.content)
    fs = []
    generator = file_service.list_directories_and_files('myshare')  # only azure
    # generator = file_service.list_directories_and_files('myshare')
    for file_or_dir in generator:
        print(file_or_dir.name)
        logging.info(file_or_dir.name)
        fs.append(file_or_dir.name)
    return jsonify(status='completed', response=fs)


@app.route('/filename', methods=['GET', 'POST'])
def filename():
    if request.method == 'POST':
        # check if the post request has the file part
        for x in request.files['file']:
            print(x)
        try:
            return jsonify(status='completed', response=request.files['file'].filename)
        except:
            return jsonify(status='uncompleted', response='something went wrong')
    else:
        return jsonify(status='uncompleted', response='no file uploaded')


@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

        # return jsonify(status='completed', response=os.path.getsize(filename))
            if app.config['DEV']:
                file_in = os.path.join(app.config['LOCAL_PATH'], f'in_{filename}')
                file.save(file_in)
            else:
                file_in = to_blob(file)

            # return jsonify(status='completed', response=file_in)
            try:
                # Create forecast object
                model = algo.Model(file.filename)
                # Model
                response = model.predict(window=0, horizon=12, slen=6)
            except Exception as err:
                print('ooops... something went wrong')
                message = ('Failed to score the model. Exception: {}'.format(err))
                response = jsonify(status='error', error_message=message)
                response.status_code = HTTP_BAD_REQUEST
            return response
    else:
        return jsonify(status='uncompleted', response='no response')


@app.route('/upload_form', methods=['GET', 'POST'])
def upload_form():
    form = FileForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash(f'File: {filename} is recieved, saving...')
            try:
                # Local dev
                file_in = os.path.join(app.config['LOCAL_PATH'], f'in_{filename}')
                file.save(file_in)
            except:
                # Azure
                file_in = to_blob(file)
        flash(f'File: {filename} is saved @ {file_in}')
        return redirect(url_for('index'))
    return render_template('upload.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


# @app.route('/login', methods=['GET', 'POST'])
# def login():

#     form = LoginForm()

#     if form.validate_on_submit():
#         return jsonify(status='success', response='form is validated')

#     return render_template('user/login.html', form=form)


# Run and debug locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8241)
