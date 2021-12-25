import hashlib
import json

import httplib2
from googleapiclient import discovery, errors


class SheetsApi:
    DISCOVERY_URL = "https://sheets.googleapis.com/$discovery/rest?version=v4"

    def __init__(self, api_key):
        self.sheets_service = discovery.build(
            "sheets",
            "v4",
            http=httplib2.Http(),
            discoveryServiceUrl=self.DISCOVERY_URL,
            developerKey=api_key,
        )

    def get_range_value(self, sheet_id, cell_range):
        """
        :return: None if an error occurred
        """
        try:
            return (
                self.sheets_service.spreadsheets()
                .values()
                .get(spreadsheetId=sheet_id, range=cell_range)
                .execute()["values"]
            )
        except errors.HttpError:
            return None

    def get_range_hash(self, sheet_id, cell_range):
        """
        :return: None if an error occurred
        """
        values = self.get_range_value(sheet_id, cell_range)
        if values is None:
            return None
        print(values)
        string = json.dumps(values).encode()
        return hashlib.md5(string).hexdigest()
