import os


# Get runtime ENV variables set in Azure API portal configuration
class Config(object):
    pass

config = Config()
config.__dict__ = {'_'.join(item.split('_')[1:]): value for item, value in os.environ.items()
                                             if item.split('_')[0] == 'APPSETTING'}
