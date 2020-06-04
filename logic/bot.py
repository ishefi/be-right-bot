from logic.bigram_model import BigramModel


class BotLogic(object):
    def __init__(self, model_uid):
        self.bm = BigramModel()
        self.bm.init_model(model_uid)

    def generate_reply(self, message_text):
        return self.bm.generate(message_text)
