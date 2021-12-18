import configparser
import argparse
import telebot


class Options:
    def __init__(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.token = config['bot']['token']

    token = None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path', help='path to the configuration file')
    args = parser.parse_args()
    return args


launch_args = parse_args()
options = Options(launch_args.config_path)
bot = telebot.TeleBot(options.token)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
