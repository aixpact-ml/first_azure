import pandas as pd


creds = pd.read_pickle('creds.pkl')

class Config(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)

config = Config(creds)

# class Config(object):
#     def __init__(self, pickl='creds.pkl'):
#         credentials = pd.read_pickle(pickl)
#         for k, v in credentials.items():
#             setattr(self, k, v)
