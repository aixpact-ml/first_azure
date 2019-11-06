import os


class Config(object):
    pass

config = Config()

try:
    # Azure runtime ENV variables set in Azure API portal configuration
    config.__dict__ = {'_'.join(item.split('_')[1:]): value
                                for item, value in os.environ.items()
                                if item.split('_')[0] == 'APPSETTING'}

except:
    # Local ENV variables set by export
    config.__dict__ = {}
