from mocks import *
from base.constants import TelegramConstants
from aws_lambda.bot import run


class TestBotLambda(BotTestCase):
    module_prefix = 'aws_lambda.bot.'

    def setUp(self):
        self.m_requests = self.patch_module('requests')
        self.bot_uid = self.unique('HAL9000')
        self.m_Bot = self.patch_module('BotLogic')
        self.m_bot = self.m_Bot.return_value

    def test_run(self):
        # given
        poor_request = 'Open the pod bay doors'
        body = {'message': {'text': poor_request,
                            'chat': {'id': '888'}
                            }
                }
        dark_answer = "I'm afraid I cannot do that"
        self.m_bot.generate_reply.return_value = dark_answer

        # when
        ret = run({'body': json.dumps(body), 'pathParameters': {'bot_id': self.bot_uid}}, None)

        # then
        self.m_Bot.assert_called_once_with(self.bot_uid)
        self.m_bot.generate_reply.assert_called_once_with(poor_request)
        self.m_requests.get.assert_called_once_with(TelegramConstants.REQ_URL.format(self.bot_uid),
                                                    params={'chat_id': 888, 'text': dark_answer})
        self.assert_contains_key_value(ret, 'statusCode', 200)
