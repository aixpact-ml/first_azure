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


# CONFIG SETTINGS
from config import config
app = Flask(__name__)
app.config.from_object(config)

HTTP_BAD_REQUEST = 400
ALLOWED_EXTENSIONS = set(['txt', 'csv'])
app.config['DEV'] = False


# Sanity check config settings
assert config.FRANK == 'test this environmental value', 'config settings failed'
assert config.FRANK == app.config['FRANK'], 'config settings failed'


# Set SECRET_KEY for Flask/wtforms
from flask_wtf.csrf import CsrfProtect
assert app.config['SECRET_KEY'] == config.SECRET_KEY, 'SECRET_KEY not set'
CsrfProtect(app)


# Flask-Mail settings via Azure ENV and below
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
assert app.config['MAIL_DEFAULT_SENDER'] == 'frank@aixpact.com', 'Flask-Mail settings failed'


from flask_mail import Mail, Message, Attachment
mail = Mail()
mail.init_app(app)


def send_email(recipients, filename):
    try:
        msg = Message('hAPIdays from AIxPact',
            sender='frank@aixpact.com',
            recipients=[recipients])
        msg.body = 'Hello ' + recipients + ',\nblahblahblah'
        msg.html = None  # render_template('email_message.html', recipients=recipients)

        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
        file = Attachment(filename=filename, content_type='text/csv')
        msg.attachment = [file]
        mail.send(msg)
    except Exception as err:
        print(err)


def _try_renderer_template(template_path, ext='txt', **kwargs):
    try:
        return render_template(f'{template_path}.{ext}', **kwargs)
    except IOError:
        pass


def deliver_email(recipients, attachments, template=None, ctx={}, *args, **kwargs):
    """
    Send a templated e-mail using a similar signature as Flask-Mail:
    http://pythonhosted.org/Flask-Mail/

    Except, it also supports template rendering. If you want to use a template
    then just omit the body and html kwargs to Flask-Mail and instead supply
    a path to a template. It will auto-lookup and render text/html messages.

    Example:
        ctx = {'user': current_user, 'reset_token': token}
        send_template_message('Password reset from Foo', ['you@example.com'],
                              template='user/mail/password_reset', ctx=ctx)

    :params: subject, recipients, body, html, sender, cc, bcc, attachments,
        reply_to, date, charset, extra_headers, mail_options, rcpt_options,
    :template: Path to a template without the extension
    :param context: Dictionary of anything you want in the template context
    :return: None
    """
    ctx = {'recipients': recipients}
    template = 'email_message'
    kwargs['body'] = _try_renderer_template(template, **ctx)
    kwargs['html'] = _try_renderer_template(template, ext='html', **ctx)
    kwargs['subject'] = 'hAPIdays from AIxPact'
    kwargs['sender'] = 'frank@aixpact.com'
    kwargs['recipients'] = [recipients]
    kwargs['attachments'] = [attachments]
    kwargs['bcc'] = ['frank@aixpact.com']

    mail.send_message(*args, **kwargs)
    return None


def _log_msg(msg):
    logging.info("{}: {}".format(datetime.datetime.now(), msg))


def allowed_file(filename):
    _log_msg('checking allowed file ...')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# try:
#     # https://docs.microsoft.com/en-us/azure/storage/files/storage-python-how-to-use-file-storage
#     from azure.storage.file import FileService, ContentSettings

#     directory_name = 'sampledir'
#     file_in = f"https://{config.STORAGE_ACCOUNT}.file.core.windows.net/myshare/myfile2"

#     file_service = FileService(
#             account_name=config.STORAGE_ACCOUNT,
#             account_key=config.ACCOUNT_KEY)
#     file_service.create_share('myshare')
#     file_service.create_directory('myshare', 'sampledir')
# except:
#     print('local debug')


def block_blob(filename):
    # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-storage-blob/12.0.0b5/azure.storage.blob.html
    SOURCE_FILE = filename
    DEST_FILE = 'something_temp.csv'
    CONTAINER = 'hapidays'

    # Instantiate a new BlobServiceClient using a connection string
    from azure.storage.blob import BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(config.BLOB_CONX)

    # Instantiate a new ContainerClient
    container_client = blob_service_client.get_container_client(CONTAINER)

    try:
        # Create new container in the service
        container_client.create_container()

        # List containers in the storage account
        list_response = blob_service_client.list_containers()
    except Exception as err:
        logging.info(f'Failed to create/list container: {err}')

    try:
        # Instantiate a new BlobClient
        blob_client = container_client.get_blob_client(SOURCE_FILE)
        # blob_client = blob_service_client.get_blob_client(CONTAINER, SOURCE_FILE)

        # [START upload_a_blob]
        # Upload content to block blob
        with open(SOURCE_FILE, "rb") as data:
            blob_client.upload_blob(data)
        # [END upload_a_blob]

        # [START download_a_blob]
        # with open(DEST_FILE, "wb") as my_blob:
        #     download_stream = blob_client.download_blob()
        #     my_blob.write(download_stream.readall())
        # [END download_a_blob]

        # [START delete_blob]
        # blob_client.delete_blob()
        # [END delete_blob]
    except Exception as err:
        logging.info(f'Failed to create blob: {err}')


def to_blob(file, container_name='hapidays', blob_name='upload.txt'):
    """"""
    # Save file to root dir in Azure - create path
    file_name = file.filename
    file.save(file_name)

    from azure.storage.blob import BlobServiceClient

    block_blob_service = BlobServiceClient(
            account_name=config.STORAGE_ACCOUNT,
            account_key=config.ACCOUNT_KEY)

    # Create blob service and container
    try:
        block_blob_service.create_container(container_name)
    except Exception as err:
        logging.info(f'Failed to create container: {err}')
        # return f'Failed to create container: {err}'

    # Upload the file from path - TODO blob_name or file_name
    blob_name = file_name
    block_blob_service.create_blob_from_path(container_name, blob_name, file_name)
    http = f"https://{config.STORAGE_ACCOUNT}.blob.core.windows.net/{container_name}/{blob_name}"
    logging.info(f'Blob upload finished @ {http}')
    return http


async def to_blob_async(file, container_name='hapidays', blob_name='upload.txt'):
    """https://pypi.org/project/azure-storage-blob/"""
    from azure.storage.blob.aio import BlobClient

    # Save file to root dir in Azure - create path
    file_name = file.filename
    file.save(file_name)
    blob_name = file_name

    # Make private - pickle file
    blob = BlobClient.from_connection_string(
        conn_str=config.BLOB_CONX,
        container_name=container_name,
        blob_name=blob_name)

    with open(file_name, "rb") as data:
        await blob.upload_blob(data)

    http = f"https://{config.STORAGE_ACCOUNT}.blob.core.windows.net/{container_name}/{blob_name}"
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
    return jsonify(status='succes', response='api is online')


@app.route("/function/<function_name>")
def function(function_name):
    """Takes some time....."""
    response = requests.get(f'http://www.aixpact.ml/api/{function_name}')
    return response.text  # jsonify(response=response.content)


@app.route("/run_function/<function_name>")
def run_function(function_name):
    """Takes some time....."""
    r = requests.get(f'http://www.aixpact.ml/api/{function_name}?name=frank')
    print(r.content, r.status_code)
    return r.text


@app.route("/secrets")
def secrets():
    import os
    # from azure.identity import DefaultAzureCredential
    # from azure.keyvault.secrets import SecretClient

    # VAULT_URL = 'https://helloaixpact-vault.vault.azure.net'
    # SECRET_ID = 'account-key'

    # credential = DefaultAzureCredential()
    # secret_client = SecretClient(vault_url=VAULT_URL, credential=credential)
    # secret = secret_client.get_secret(SECRET_ID)
    # return jsonify(status='succes', response={'secret_name': secret.name, 'secret_value': secret.value})
    return {'_'.join(item.split('_')[1:]): value for item, value in os.environ.items()
                                             if item.split('_')[0] == 'APPSETTING'}
    # return {item: value for item, value in os.environ.items()}


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
                file_in = os.path.join(config.LOCAL, f'in_{filename}')
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
        email = form.email.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash(f'File: {filename} is recieved, saving...')
            try:
                # Local dev
                file_in = os.path.join(config.LOCAL, f'in_{filename}')
                file.save(file_in)
            except:
                # Azure
                ext = '.' + filename.split('.')[-1]
                blob_name = email.replace('@', '_').replace('.', '_').replace('-', '_') + ext
                file.save(blob_name)
                block_blob(blob_name)
                file_in = blob_name  # to_blob(file, blob_name=blob_name)
        flash(f'thank you an email has been sent to: {email} with attachment: {file_in}')
        # deliver_email(recipients=email, attachments=file_in)
        send_email(email, file_in)
        return redirect(url_for('thankyou', message=file_in))
        flash(f'Try again.....')
    return render_template('upload.html', form=form)


@app.route("/thankyou")
def thankyou():
    return jsonify(status='succes', response=request.args.get('message'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
        flash('form is validated')
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


# Run and debug locally in Jupyter
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8241)
