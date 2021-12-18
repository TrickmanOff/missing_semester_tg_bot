from peewee import Model, SqliteDatabase, TextField


class DataStorage:
    def __init__(self, db_path):
        self.db = SqliteDatabase(db_path)

        class BaseModel(Model):
            class Meta:
                database = self.db

        class Record(BaseModel):
            chat_id = TextField()
            name = TextField()
            sheet_id = TextField()
            range = TextField()
            old_value_hash = TextField()

        self.Record = Record

        self.db.connect()
        self.db.create_tables([self.Record])
        self.db.commit()
        self.db.close()

    def find_by_props(self, chat_id, sheet_id, cell_range):
        """
        :return: name of the notifier if found
                 None if not found
        """
        self.db.connect()
        same_record = self.Record.select().where(
            (self.Record.chat_id == chat_id)
            & (self.Record.sheet_id == sheet_id)
            & (self.Record.range == cell_range)
        )

        res = None if len(same_record) == 0 else same_record.get().name
        self.db.close()
        return res

    def find_by_name(self, chat_id, name):
        """
        :return: True or False
        """
        self.db.connect()
        record = self.Record.select().where(
            (self.Record.chat_id == chat_id) & (self.Record.name == name)
        )
        res = len(record) > 0
        self.db.close()
        return res

    def delete_with_name(self, chat_id, name):
        """
        :return: True   if deleted
                 False  if not found
        """
        self.db.connect()
        record = self.Record.select().where(
            (self.Record.chat_id == chat_id) & (self.Record.name == name)
        )
        if len(record) == 0:
            return False
        else:
            record.get().delete_instance()
            self.db.commit()
            self.db.close()
            return True

    def add_record(self, chat_id, name, sheet_id, cell_range, old_hash_value="---"):
        """
        :return: True if successfully set
                 False otherwise
        """
        self.db.connect()
        # print('old_hash:\t', old_hash_value)
        new_record = self.Record.create(
            chat_id=chat_id,
            name=name,
            sheet_id=sheet_id,
            range=cell_range,
            old_value_hash=old_hash_value,
        )
        new_record.save()
        self.db.commit()
        self.db.close()

    @staticmethod
    def transform_to_dict(records):
        return [
            {
                "chat_id": rec.chat_id,
                "name": rec.name,
                "sheet_id": rec.sheet_id,
                "range": rec.range,
                "old_value_hash": rec.old_value_hash,
            }
            for rec in records
        ]

    def records_by_user(self, chat_id):
        self.db.connect()

        records = self.transform_to_dict(
            self.Record.select().where(self.Record.chat_id == chat_id)
        )
        self.db.close()
        return records

    def get_all_records(self):
        self.db.connect()
        all_records = self.transform_to_dict(self.Record.select())
        self.db.close()
        return all_records
