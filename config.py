import pandas as pd


def get_blob(container_name='config', blob_name='creds.pkl', path='creds.pkl'):
    """"""
    from azure.storage.blob import BlockBlobService

    storageAccount = 'helloaixpact'
    accountKey = '/K/UXeclbEGQ6qxVEEXLrD47hwrxHGJGJnpGPVNZXu2dEEhJWSJ9G4+iDsvWDx4IfDYpIBW9OM+EX/4iNFbR1g=='

    block_blob_service = BlockBlobService(
        account_name=storageAccount, account_key=accountKey)

    # Save blob to local disk @ path
    block_blob_service.get_blob_to_path(container_name, blob_name, path)
    return pd.read_pickle(path)


class Config(object):
    pass

config = Config()
config.__dict__ = get_blob()
