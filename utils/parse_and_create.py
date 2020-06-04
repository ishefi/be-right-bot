#!/usr/bin/env python

import argparse
import os
import sys
from collections import namedtuple

from logic.model_creator import ModelCreatorLogic

BASE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(BASE)

MESSAGE_RE = r'(\d+\/\d+\/\d+, \d\d:\d\d) - (.*): ([.|\n]*)'

DATETIME = r'\d+\/\d+\/\d\d, \d\d:\d\d - '
SENDER_TEXT = r'([^:]*): (.*)'

parser = argparse.ArgumentParser(description='Create model for bot')
parser.add_argument('-i', '--input', type=str, required=True, help='WhatsApp conversation .txt file')
parser.add_argument('-b', '--bot-token', type=str, required=False, help='Token of the bot. If not provided, creates a new bot')


Message = namedtuple('Message', ['sender', 'text'])


def main():
    args = parser.parse_args()
    with open(args.input) as f:
        chat = f.read()
    creator = ModelCreatorLogic(args.bot_token)
    creator.split_chat(chat)

    prompt = 'Who is this bot is going to imitate?'
    for i, sender in enumerate(creator.speakers, start=1):
        prompt += '\n{}. {}'.format(i, sender)

    speakers = list(creator.speakers)

    choice = get_choice(prompt, [str(i) for i in range(1, len(speakers) + 1)]) - 1

    speaker = speakers[choice]

    print("Getting relevant messages...")
    relevant_messages = creator.get_user_messages(speaker)

    print("Creating model...")
    creator.build_and_save_model(relevant_messages)
    print("Setting webhook...")
    creator.set_webhook()
    print("Done")


def get_choice(prompt, options):
    while True:
        choice = input(prompt)
        if choice in options:
            return int(choice)


if __name__ == '__main__':
    main()
