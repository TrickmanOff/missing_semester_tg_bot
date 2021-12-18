"""
Simple echo-bot
"""
import argparse
import configparser

import telebot


def parse_options(config_path):
    """Extract necessary options from the config file"""
    config = configparser.ConfigParser()
    config.read(config_path)
    return {"token": config["bot"]["token"]}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="path to the configuration file")
    args = parser.parse_args()
    return args


launch_args = parse_args()
options = parse_options(launch_args.config_path)
bot = telebot.TeleBot(options["token"])


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
