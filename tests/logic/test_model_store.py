from mocks import *
from logic.model_store import ModelStore


class TestModelStore(BotTestCase):
    module_prefix = 'logic.model_store.'

    def setUp(self):
        self.m_boto = self.patch_module('boto')
        self.m_connect = self.m_boto.s3.connect_to_region
        self.m_get_bucket = self.m_connect.return_value.get_bucket
        self.m_bucket = self.m_get_bucket.return_value = MagicMock()
        self.m_Key = self.patch_module('Key')
        self.m_key = self.m_Key.return_value
        self.content = {'content': 'wow'}
        self.m_key.get_contents_as_string.return_value = json.dumps(self.content)

        self.model_uid = self.unique('bot:bot')
        self.testee = ModelStore(self.model_uid)

    def test_correct_bucket(self):
        # given setUp
        # then
        self.m_connect.assert_called_once_with(
            region_name=self.m_config.aws['region'],
            aws_access_key_id=self.m_config.aws['access_key_id'],
            aws_secret_access_key=self.m_config.aws['secret_access_key']
        )
        self.m_get_bucket.assert_called_once_with(self.testee.BUCKET)
        self.assertEqual(self.testee.bucket, self.m_bucket)

    def test_get_corpus(self):
        # when
        corpus = self.testee.get_corpus()

        # then
        self.assertEqual(corpus, self.content)
        self.m_Key.assert_called_once_with(self.m_bucket)
        self.m_key.get_contents_as_string.assert_called_once_with(encoding='utf-8')
        self.assertEqual(self.m_key.key, f'corpus{self.model_uid}.json')

    def test_get_model(self):
        # when
        model = self.testee.get_model()

        # then
        self.assertEqual(model, self.content)
        self.m_Key.assert_called_once_with(self.m_bucket)
        self.m_key.get_contents_as_string.assert_called_once_with(encoding='utf-8')
        self.assertEqual(self.m_key.key, f'model{self.model_uid}.json')

    def test_save_corpus(self):
        # when
        self.testee.save_corpus(self.content)

        # then
        self.m_Key.assert_called_once_with(self.m_bucket)
        self.m_key.set_contents_from_string.assert_called_once_with(self.content)
        self.assertEqual(self.m_key.key, f'corpus{self.model_uid}.json')

    def test_save_model(self):
        # when
        self.testee.save_model(self.content)

        # then
        self.m_Key.assert_called_once_with(self.m_bucket)
        self.m_key.set_contents_from_string.assert_called_once_with(self.content)
        self.assertEqual(self.m_key.key, f'model{self.model_uid}.json')

