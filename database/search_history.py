from peewee import *
from peewee import SqliteDatabase

db: SqliteDatabase = SqliteDatabase(r'database\history.db')


class SearchHistory(Model):
    user_id = IntegerField(null=True)
    user_name = TextField(null=True)
    command = TextField(null=True)
    date = DateField(null=True)
    time = TimeField(null=True)
    search_results = TextField(null=True)

    class Meta:
        database = db


SearchHistory.create_table()


def save_result_to_db(data_lst):
    prepare_data_for_save = [
        '\n'.join(data[0][:-1])
        for data in data_lst]

    save_to_data = '\n\n'.join(prepare_data_for_save)

    return save_to_data
