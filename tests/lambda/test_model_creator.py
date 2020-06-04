from mocks import *
from aws_lambda.model_creator import run


class TestModelCreatorLambda(BotTestCase):
    module_prefix = 'aws_lambda.model_creator.'

    def setUp(self):
        self.bot_uid = self.unique('HAL9000')
        self.m_ModelCreator = self.patch_module('ModelCreatorLogic')
        self.m_model_creator = self.m_ModelCreator.return_value

    def test_run(self):
        # given
        self.m_model_creator.get_user_messages.return_value = 'Maybe the dingo ate your baby'
        self.m_model_creator.set_webhook.return_value = 222

        # when
        ret = run({'body': json.dumps({'token': self.bot_uid,
                                       'speaker': 'Elaine',
                                       'text': 'dingo, yada-yada, vandelay'})},
                  None)

        # then
        self.m_ModelCreator.assert_called_once_with(self.bot_uid)
        self.m_model_creator.split_chat.assert_called_once_with('dingo, yada-yada, vandelay')
        self.m_model_creator.get_user_messages.assert_called_once_with('Elaine')
        self.m_model_creator.build_and_save_model.assert_called_once_with('Maybe the dingo ate your baby')
        self.m_model_creator.set_webhook.assert_called_once_with()
        self.assert_contains_key_value(ret, 'statusCode', 222)
