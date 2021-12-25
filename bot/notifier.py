import time

import schedule
from data_storage import DataStorage
from sheets_api import SheetsApi
from utils import formatted_link_from_id

DISCOVERY_URL = "https://sheets.googleapis.com/$discovery/rest?version=v4"
CHECK_FREQUENCY = 10

"""
data format:

    chat_id:
    name:
    sheet_id:
    range:
    old_value_hash:
"""


def notify(bot, db_storage, db_lock, sheets_service):
    db_lock.acquire()

    removed = []
    for record in db_storage.get_all_records():
        cur_values_hash = sheets_service.get_range_hash(
            record["sheet_id"], record["range"]
        )
        if cur_values_hash is None:
            message_text = (
                f"An error occurred during a check of the <b>{record['name']}</b> "
                f"notifier. Probably the "
                f"{formatted_link_from_id(record['sheet_id'], 'table')} "
                f"is private or doesn't exist."
            )
            bot.send_message(
                chat_id=record["chat_id"],
                text=message_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            removed.append((record["chat_id"], record["name"]))
            continue

        print("new hash\t", cur_values_hash)
        if cur_values_hash != record["old_value_hash"]:
            message_text = (
                f"An update found for the notifier <b>{record['name']}</b>\n"
                f"table link:\t{formatted_link_from_id(record['sheet_id'])}\n"
                f"range:\t\t{record['range']}"
            )
            bot.send_message(
                chat_id=record["chat_id"],
                text=message_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            removed.append((record["chat_id"], record["name"]))

    for chat_id, name in removed:
        db_storage.delete_with_name(chat_id, name)
        message_text = f"The notifier <b>{name}</b> has been disabled"
        bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode="HTML",
        )

    db_lock.release()


def start_notifier(bot_factory, db_path, db_lock, sheets_api_key):
    bot = bot_factory.create_bot()
    db_storage = DataStorage(db_path)
    sheets_service = SheetsApi(sheets_api_key)
    print("Notifier has been set")

    schedule.every(CHECK_FREQUENCY).seconds.do(
        notify, bot, db_storage, db_lock, sheets_service
    )
    while True:
        schedule.run_pending()
        time.sleep(1)
