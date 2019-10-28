import requests
import os
from flask import (Flask, Blueprint, redirect, request, flash, url_for, jsonify,
                   render_template, session, current_app, make_response,
                   send_file, send_from_directory)
from werkzeug.utils import secure_filename

import code

app = Flask(__name__)

HTTP_BAD_REQUEST = 400
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
SHARED = 'https://helloaixpact.file.core.windows.net/'
app.config['SHARED'] = SHARED


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    """"""
    r = requests.get('http://www.aixpact.ml/api/httptrigger?name=frank')
    # print(r.content, r.status_code)
    return r.text


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
            file_in = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_in)
            try:
                # Create forcast object
                file_out = os.path.join(
                    app.config['SHARED'], 'forecast.csv')
                model = code.Model(filename=file_in, sep=',', header=0, filename_out=file_out)
                # Model
                response = model.predict(window=0, horizon=12, slen=6)
            except Exception as err:
                print('ooops... something went wrong')
                message = ('Failed to score the model. Exception: {}'.format(err))
                response = jsonify(status='error', error_message=message)
                response.status_code = HTTP_BAD_REQUEST
            # FTUP(file_out)
            return send_from_directory(app.config['SHARED'],
                                       'forecast.csv', as_attachment=True)
            # return jsonify(status='completed', response=response)
