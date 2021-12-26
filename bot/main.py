import argparse
import re
from multiprocessing import Lock, Process

from bot_factory import BotFactory
from data_storage import DataStorage
from notifier import CHECK_FREQUENCY, start_notifier
from sheets_api import SheetsApi
from tabulate import tabulate
from utils import formatted_link, formatted_link_from_id, id_from_link


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
        text = message.text
        args_patterns = ['/set "[^"]*"', ' [^" ]*', ' "[^"]*"']
        args = []

        for pattern in args_patterns:
            enter = re.match(pattern, text)
            if enter is None:
                bot.reply_to(message, text="Wrong format")
                return

            enter = enter.group(0)
            args.append(enter)
            text = text[len(enter) :]

        name = args[0].split('"')[-2]
        sheet_id = args[1][1:]
        cell_range = args[2][2:-1]

        if len(sheet_id) > 44:  # interpret as an url
            sheet_id = id_from_link(sheet_id)
            if sheet_id is None:
                bot.reply_to(message, "Invalid URL")
                return

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
            db_lock.release()
            return
        if db_storage.find_by_name(chat_id, name):
            bot.reply_to(message, "A notifier with this name is already set")
            db_lock.release()
            return

        cur_value_hash = sheets_service.get_range_hash(sheet_id, cell_range)
        if cur_value_hash is None:
            message_text = (
                f"An error occurred trying to set the <b>{name}</b> "
                f"notifier. \n"
                f"Check the Sheet ID and range format. "
                f"Probably the {formatted_link_from_id(sheet_id, 'table')} is "
                f"private or doesn't exist. "
            )
            bot.send_message(
                chat_id=chat_id,
                text=message_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            db_lock.release()
            return
        # add new notifier
        db_storage.add_record(
            chat_id,
            name,
            sheet_id,
            cell_range,
            cur_value_hash,
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
        if len(message.text) < 6:
            bot.reply_to(message, text="Wrong format")
            return

        db_lock.acquire()

        name = message.text[5:]
        if db_storage.delete_with_name(message.chat.id, name):
            message_text = f"The notifier <b>{name}</b> has been deleted"
        else:
            message_text = f"The notifier <b>{name}</b> not found"
        bot.reply_to(message, text=message_text, parse_mode="HTML")
        db_lock.release()

    @bot.message_handler(commands=["help"])
    def help_command(message):
        a1_examples_link = (
            "https://developers.google.com/sheets/api/guides/concepts#expandable-1"
        )
        r1c1_examples_link = (
            "https://developers.google.com/sheets/api/guides/concepts#expandable-2"
        )

        message_text = (
            "To <b>set</b> a notifier enter a message in the following format:\n"
            '<pre> /set "{name}" {google_sheet_id | table_url} "{cell range}" </pre>\n'
            f"cell range format - {formatted_link(a1_examples_link, 'A1')} "
            f"or {formatted_link(r1c1_examples_link, 'R1C1')} notation\n"
            "for example:\n"
            '<pre> /set "test results" 17h7GKuJ1gS7faOiyM7dBaM1XPUHPXPgIb7zCFfFGUOE '
            '"My Sheet!A1:A2" </pre>\n'
            '<pre> /set "test results" '
            "https://docs.google.com/spreadsheets/d/17h7GKuJ1gS7faOiyM7dBaM1XPUHPXPgIb7zCFfFGUOE "
            '"My Sheet!A1:A2" </pre>\n\n'
            ""
            "To <b>delete</b> a notifier use\n"
            "<pre> /del {name} </pre>\n"
            "for example:\n"
            "<pre> /del test results </pre>"
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=message_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

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
