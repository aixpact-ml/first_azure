import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    BLOB_CONN = "DefaultEndpointsProtocol=https;AccountName=helloaixpact;AccountKey=/K/UXeclbEGQ6qxVEEXLrD47hwrxHGJGJnpGPVNZXu2dEEhJWSJ9G4+iDsvWDx4IfDYpIBW9OM+EX/4iNFbR1g==;EndpointSuffix=core.windows.net"
