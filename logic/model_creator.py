import attr
import re
import requests

from base import config
from base.constants import TelegramConstants
from logic.bigram_model import BigramModel


@attr.s
class Message(object):
    speaker = attr.ib()
    text = attr.ib()


class ModelCreatorLogic(object):
    DATETIME = re.compile(r'\[?\d{1,2}[/.]\d{1,2}[/.]\d{2,4}, \d{1,2}:\d{2}(?::\d{1,2})?(?: (?:AM|PM))?\]?(?: -)? ')
    SENDER_TEXT = re.compile(r'([^:]*): (.*)', flags=re.S)

    def __init__(self, model_uid):
        self.model_uid = model_uid
        self.messages = []
        self.speakers = set()

    @staticmethod
    def datetime_split(chat):
        return ModelCreatorLogic.DATETIME.split(chat)

    def split_chat(self, chat):
        """Splits WhatsApp chat into speakers and Messages.

        Args:
            chat (str): Text of exported WhatsApp chat.

        Returns:
            None. Populates `self.speakers` and `self.messages` with
            `chat`'s data.
        """
        senders_messages = self.datetime_split(chat)
        for sender_message in senders_messages:
            message = self._get_message(sender_message)
            if message:
                self.messages.append(message)
                self.speakers.add(message.speaker)

    def _get_message(self, sender_message):
        # type: (str) -> Message or None
        """Creates a Message out of WhatsApp chat line.

        Args:
            sender_message (str): WhatsApp chat line.

        Returns:
            Message where `speaker` is `sender_message`'s speaker and `text` is
            `sender_message`'s text. Returns None if format is wrong.

        Examples:
            >>> self._get_message('10/19/13, 20:09 - itamar: Hi')
            Message(speaker='itamar', text='Hi')
            >>> self._get_message('WRONG FORMAT')
            <None>
        """
        st_re = self.SENDER_TEXT.search(sender_message)
        if st_re is None:
            return None
        else:
            return Message(speaker=st_re.group(1), text=st_re.group(2).strip())

    def get_user_messages(self, speaker):
        # type: (str) -> [Message]
        """Returns all messages of `speaker`.

        Args:
            speaker (str): Speaker whose messages we want.

        Returns:
            List of Messages whose `.speaker` is `speaker`.

        """
        return list(filter(lambda m: m.speaker == speaker, self.messages))

    def build_and_save_model(self, messages):
        bigram_model = BigramModel()
        bigram_model.train_string(self._clean_text_from_messages(messages))
        bigram_model.set_model_uid(self.model_uid)
        bigram_model.save_model()

    def _clean_text_from_messages(self, msgs):
        return '\n'.join(m.text.replace('<Media omitted>', '') for m in msgs)

    def set_webhook(self):
        response = requests.post(
            TelegramConstants.TELEGRAM_WEBHOOK.format(self.model_uid),
            json={'url': config.app_url.format(self.model_uid)}
        )
        return response.status_code
