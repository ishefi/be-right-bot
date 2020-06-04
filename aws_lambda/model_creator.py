import json

from base.logger import logger
from logic.model_creator import ModelCreatorLogic


def run(event, context):
    body = json.loads(event['body'])
    logic = ModelCreatorLogic(body['token'])
    logic.split_chat(body['text'])
    speaker = body['speaker']
    logger.info('Creating bot for %s', speaker)
    speaker_messages = logic.get_user_messages(speaker)
    logic.build_and_save_model(speaker_messages)
    logger.info('Created bot. Saving webhook...')
    webhook_response = logic.set_webhook()
    return {'statusCode': webhook_response}
