import os
import logging


class Config(object):
    pass

config = Config()

if os.getcwd() != '/home/jovyan/aixpact/_first_azure':
    # Azure runtime ENV variables set in Azure API portal configuration
    config.__dict__ = {'_'.join(item.split('_')[1:]): value
                                for item, value in os.environ.items()
                                if item.split('_')[0] == 'APPSETTING'}

else:
    # Local ENV variables set by export
    assert os.getcwd() == '/home/jovyan/aixpact/_first_azure'
    from .env.local_env import az_settings
    config.__dict__ = {**{item['name']: item['value'] for item in az_settings}, **{'WTF_CSRF_CHECK_DEFAULT': False}}


def test():
    print(az_settings['MAIL_DEFAULT_SENDER'])
