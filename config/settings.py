import os
import logging


class Config(object):
    pass

config = Config()

cwd = '/_first_azure'

if os.getcwd() != cwd:
    # Azure runtime ENV variables set in Azure API portal configuration
    # Azure ENV variables start with: APPSETTING_
    config.__dict__ = {'_'.join(item.split('_')[1:]): value
                                for item, value in os.environ.items()
                                if item.split('_')[0] == 'APPSETTING'}

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.environ['APPSETTING_GOOGLE_APPLICATION_CREDENTIALS']
    os.environ['DIALOGFLOW_PROJECT_ID'] = os.environ['APPSETTING_DIALOGFLOW_PROJECT_ID']

    # Save dialogFlow creds form Azure ENV - keep out of github - link in .env
    try:
        file = os.environ['GOOGLE_CREDS_FILE']
        path = os.path.join(os.getcwd(), file)
        with open(path, 'w') as f:
            f.write(os.environ['APPSETTING_GOOGLE_APPLICATION_CREDENTIALS'])
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
            logging.info(os.environ['APPSETTING_GOOGLE_APPLICATION_CREDENTIALS'])
            logging.info(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
            logging.info(f'created dialogflow creds file: {err}')
    except Exception as err:
        logging.info(f'failed to create dialogflow creds file: {err}')

else:
    # Local ENV variables set by export
    assert os.getcwd() == cwd
    from .env.local_env import az_settings, GOOGLE_APPLICATION_CREDENTIALS, DIALOGFLOW_PROJECT_ID
    config.__dict__ = {**{item['name']: item['value'] for item in az_settings},
                       **{'WTF_CSRF_CHECK_DEFAULT': False},
                       **{'DIALOGFLOW_PROJECT_ID': DIALOGFLOW_PROJECT_ID},
                       **{'GOOGLE_APPLICATION_CREDENTIALS': GOOGLE_APPLICATION_CREDENTIALS}
                       }

logging.info(f'DEBUG settings: {type(config)} {config}')

def test():
    print(az_settings['MAIL_DEFAULT_SENDER'])
