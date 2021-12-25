import telebot


class BotFactory:
    def __init__(self, token):
        self.token = token

    def create_bot(self):
        return telebot.TeleBot(self.token)
