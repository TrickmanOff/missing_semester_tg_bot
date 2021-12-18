def link_from_id(sheet_id):
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}"


def formatted_link_from_id(sheet_id):
    return f'<a href="{link_from_id(sheet_id)}">click</a>'
