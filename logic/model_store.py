import boto
import json
from boto.s3.key import Key

from base import config


class ModelStore(object):
    BUCKET = 'telebot-models'

    def __init__(self, model_uid):
        self.model_uid = model_uid
        self.bucket = self._bucket()

    def get_model(self):
        return self._get_from_s3('model')

    def get_corpus(self):
        return self._get_from_s3('corpus')

    def _get_from_s3(self, which):
        bucket_key = self._get_key(which)
        return json.loads(bucket_key.get_contents_as_string(encoding='utf-8'))

    def save_model(self, string):
        return self._save_to_s3('model', string)

    def save_corpus(self, string):
        return self._save_to_s3('corpus', string)

    def _save_to_s3(self, which, string):
        bucket_key = self._get_key(which)
        bucket_key.set_contents_from_string(string)

    def _get_key(self, which):
        bucket_key = Key(self.bucket)
        bucket_key.key = f'{which}{self.model_uid}.json'
        return bucket_key

    def _bucket(self):
        conn = boto.s3.connect_to_region(
            region_name=config.aws['region'],
            aws_access_key_id=config.aws['access_key_id'],
            aws_secret_access_key=config.aws['secret_access_key'])
        return conn.get_bucket(self.BUCKET)
