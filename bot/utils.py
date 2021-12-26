import re


def link_from_id(sheet_id):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}"


def formatted_link(link, text):
    return f'<a href="{link}">{text}</a>'


def formatted_link_from_id(sheet_id, text="click"):
    return formatted_link(link_from_id(sheet_id), text)


def id_from_link(link):
    pattern = r"docs\.google\.com/spreadsheets/.*/[a-zA-Z0-9-_]{44}"
    match = re.search(pattern, link)
    if match is None:
        return None
    else:
        return match.group(0)[-44:]
