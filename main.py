"""
Simple echo-bot
"""
import argparse

import telebot


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_path", help="path to the configuration file")
    parser.add_argument("token")
    args = parser.parse_args()
    return args


launch_args = parse_args()
print(f"Starting bot with token:\t{launch_args.token}")
bot = telebot.TeleBot(launch_args.token)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
