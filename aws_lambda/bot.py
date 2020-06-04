import json

import requests

from base.constants import TelegramConstants
from base.logger import logger
from logic.bot import BotLogic


def run(event, context):
    try:
        bot_id = event['pathParameters']['bot_id']
        body = json.loads(event.get('body', {}))
        message = body.get('message', {})
        bot_logic = BotLogic(bot_id)
        reply = bot_logic.generate_reply(message.get('text', ''))
        chat_id = message['chat']['id']
        requests.get(TelegramConstants.REQ_URL.format(bot_id),
                     params={'chat_id': int(chat_id), 'text': reply})
    except Exception as ex:
        logger.exception(ex)
    return {'statusCode': 200}
