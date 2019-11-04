import pandas as pd


class Config(object):
    pass

config = Config()
config.__dict__ = pd.read_pickle('creds.pkl')
