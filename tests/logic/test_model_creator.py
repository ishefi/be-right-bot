from mocks import *
from base.constants import TelegramConstants
from logic.model_creator import Message
from logic.model_creator import ModelCreatorLogic


class TestModelCreator(BotTestCase):
    module_prefix = 'logic.model_creator.'

    def setUp(self):
        self.eggplant = '🍆'
        self.noa = 'noa'
        self.m_BM = self.patch_module('BigramModel')
        self.m_bm = self.m_BM.return_value
        self.m_requests = self.patch_module('requests')
        self.message1 = Message(speaker=self.eggplant, text='say something')
        self.message2 = Message(speaker=self.eggplant, text='did your TA talk about fields?')
        self.message3 = Message(speaker=self.noa, text='only in the last minutes. On the rules')
        self.message4 = Message(speaker=self.noa, text='download Community for next Monday!')
        self.chat = self.mkchat()
        self.model_uid = self.unique('ModelAyeDee')

        self.testee = ModelCreatorLogic(self.model_uid)

    def mkchat(self):
        return f'''
10/19/13, 20:09 - {self.message1.speaker}: {self.message1.text}
10/19/13, 20:09 - {self.message2.speaker}: {self.message2.text} 
10/19/13, 20:19 - {self.message3.speaker}: {self.message3.text}
10/19/13, 20:20 - {self.message4.speaker}: {self.message4.text}'''

    def test_message_split(self):
        # when
        self.testee.split_chat(self.chat)

        # then
        self.assertSetEqual(self.testee.speakers, {self.eggplant, self.noa})
        self.assertCountEqual(self.testee.messages, [self.message1,
                                                     self.message2,
                                                     self.message3,
                                                     self.message4])

    def test_message_split__with_eol(self):
        # given
        self.message1.text = 'hello\nnurse'
        chat = self.mkchat()

        # when
        self.testee.split_chat(chat)

        # then
        self.assertIn(self.message1, self.testee.messages)

    def test_get_user_messages(self):
        # given
        self.testee.messages = [self.message1, self.message3, self.message4, self.message2]
        self.testee.speakers = {self.eggplant, self.noa}

        # when
        messages = self.testee.get_user_messages(self.eggplant)

        # then
        self.assertCountEqual(messages, [self.message1, self.message2])

    def test_build_and_save_model(self):
        # given
        messages = [self.message1, self.message2, self.message3, self.message4]
        texts = '\n'.join(m.text for m in messages)

        # when
        self.testee.build_and_save_model(messages)

        # then
        self.m_BM.assert_called_once_with()
        self.m_bm.train_string.assert_called_once_with(texts)
        self.m_bm.set_model_uid.assert_called_once_with(self.model_uid)
        self.m_bm.save_model.assert_called_once()

    def test_build_and_save_model__no_media(self):
        # given
        message1 = Message(speaker='1', text='Hi<Media omitted>')
        message2 = Message(speaker='1', text='<Media omitted>Hello')

        # when
        self.testee.build_and_save_model([message1, message2])

        # then
        self.m_bm.train_string.assert_called_once_with('Hi\nHello')

    def test_model_set_webhook(self):
        # when
        self.testee.set_webhook()

        # then
        self.m_requests.post.assert_called_once_with(
            TelegramConstants.TELEGRAM_WEBHOOK.format(self.model_uid),
            json={'url': self.m_config.app_url.format(self.model_uid)}
        )


class TestModelCreatorTimeSplit(BotTestCase):
    @classmethod
    def setUpClass(cls):
        cls.leia_message = 'Leia <3: I love you\n'
        cls.han_message = 'Han: I know\n'

    def assert_can_split_text(self, text):
        split = ModelCreatorLogic.datetime_split(text)
        self.assertEqual(split, ['', self.leia_message, self.han_message])

    def test_datetime_split__whatsapp_android_format(self):
        # given
        text = f'11/20/13, 19:11 - {self.leia_message}11/20/13, 19:12 - {self.han_message}'
        # when, then
        self.assert_can_split_text(text)

    def test_datetime_split__whatsapp_android_format__with_seconds(self):
        # given
        text = f'11/20/2013, 9:11:50 - {self.leia_message}11/20/2013, 19:12:20 - {self.han_message}'
        # when, then
        self.assert_can_split_text(text)

    def test_datetime_split__whatsapp_android_format__AMPM(self):
        # given
        text = f'11/20/2013, 9:11 AM - {self.leia_message}11/20/2013, 12:12 PM - {self.han_message}'
        # when, then
        self.assert_can_split_text(text)

    def test_datetime_split__whatsapp_iphone_format(self):
        # given
        text = f'[11/20/13, 19:11] {self.leia_message}[11/20/13, 19:12] {self.han_message}'
        # when, then
        self.assert_can_split_text(text)
