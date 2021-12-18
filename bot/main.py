"""
Simple echo-bot
"""
import argparse
from multiprocessing import Lock, Process

from bot_factory import BotFactory
from data_storage import DataStorage
from notifier import CHECK_FREQUENCY, start_notifier
from sheets_api import SheetsApi
from tabulate import tabulate
from utils import formatted_link_from_id


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("config_path", help="path to the configuration file")
    parser.add_argument("token", help="telegram bot token")
    parser.add_argument("api_key", help="google sheets api key")
    parser.add_argument("db_path", help="notifiers database filepath")
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    launch_args = parse_args()

    bot_factory = BotFactory(launch_args.token)
    bot = bot_factory.create_bot()

    db_path = launch_args.db_path
    db_storage = DataStorage(db_path)
    db_lock = Lock()

    sheets_service = SheetsApi(launch_args.api_key)

    @bot.message_handler(commands=["set"])
    def set_command(message):
        if len(message.text.split(" ")) != 4:
            bot.send_message(chat_id=message.chat.id, text="Wrong format")
        else:
            _, name, sheet_id, cell_range = message.text.split(" ")
            chat_id = message.chat.id

            db_lock.acquire()

            with_same_props = db_storage.find_by_props(chat_id, sheet_id, cell_range)
            if with_same_props is not None:
                if with_same_props != name:
                    message_text = (
                        f"The notifier '{with_same_props}' has the same properties"
                    )
                else:
                    message_text = "Already set"
                bot.reply_to(message, message_text)
                return
            if db_storage.find_by_name(chat_id, name):
                bot.reply_to(message, "A notifier with this name is already set")
                return

            # add new notifier
            db_storage.add_record(
                chat_id,
                name,
                sheet_id,
                cell_range,
                sheets_service.get_range_hash(sheet_id, cell_range),
            )
            bot.reply_to(message, text="Successfully set")
            db_lock.release()

    @bot.message_handler(commands=["list"])
    def list_command(message):
        db_lock.acquire()

        records = db_storage.records_by_user(message.chat.id)

        headers = ["Name", "Cell Range"]

        data = [[rec["name"], rec["range"]] for rec in records]
        tabulated_text = tabulate(data, headers=headers)

        message_text = ""

        for line, sheet_id in zip(
            tabulated_text.split("\n"), ["", ""] + [rec["sheet_id"] for rec in records]
        ):
            line = "<pre>" + line + "</pre>"
            link = ""
            if sheet_id != "":
                link = formatted_link_from_id(sheet_id)
            message_text += line + "    " + link + "\n"

        bot.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
        db_lock.release()

    @bot.message_handler(commands=["del"])
    def del_command(message):
        db_lock.acquire()
        if len(message.text.split(" ")) != 2:
            bot.reply_to(message, text="Wrong format")
            return

        name = message.text.split(" ")[1]
        if db_storage.delete_with_name(message.chat.id, name):
            message_text = f"The notifier '{name}' has been deleted"
        else:
            message_text = f"The notifier '{name}' not found"
        bot.reply_to(message, text=message_text)
        db_lock.release()

    @bot.message_handler(commands=["help"])
    def help_command(message):
        message_text = (
            "For setting a notification enter a message in the following format\n"
            "'/set <name> <google_sheet_id> <cell range>' "
            "(each value must not contain spaces)\n"
            "cell range format - A1 or R1C1 notation\n"
            "for example:\n"
            "'/set test_results 17h7GKuJ1gS7faOiyM7dBaM1XPUHPXPgIb7zCFfFGUOE "
            "Sheet1!A1:A2'"
        )
        bot.send_message(chat_id=message.chat.id, text=message_text)

    @bot.message_handler(commands=["check_frequency"])
    def check_freq_command(message):
        bot.send_message(
            chat_id=message.chat.id,
            text=f"Current update frequency is {CHECK_FREQUENCY} seconds",
        )

    notifier_process = Process(
        target=start_notifier, args=(bot_factory, db_path, db_lock, launch_args.api_key)
    )
    notifier_process.start()

    print(f"Bot started with token{launch_args.token}")
    bot.infinity_polling()
