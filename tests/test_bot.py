from mocks import *
from logic.bot import BotLogic


class TestBotLogic(BotTestCase):
    module_prefix = 'logic.bot.'

    def setUp(self):
        self.m_BigramModel = self.patch_module('BigramModel')
        self.m_bigram_model = self.m_BigramModel.return_value
        self.model_uid = self.unique('Airplane!')
        self.testee = BotLogic(self.model_uid)

    def test_generate(self):
        # given
        generated = 'Helloooooooo nurse'
        self.m_bigram_model.generate.return_value = generated

        # when
        reply = self.testee.generate_reply('GIVEN')

        # then
        self.assertEqual(generated, reply)
        self.m_BigramModel.assert_called_once_with()
        self.m_bigram_model.init_model.assert_called_once_with(self.model_uid)
        self.m_bigram_model.generate.assert_called_once_with('GIVEN')