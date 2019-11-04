import pandas as pd


class Config(object):
    def __init__(self, pickl='creds.pkl'):
        credentials = pd.read_pickle(pickl)
        for k, v in credentials.items():
            setattr(self, k, v)
