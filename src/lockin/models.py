from peewee import SqliteDatabase, CharField, Model
from settings import DB_URI

class Credentials(Model):
    service = CharField()
    username = CharField()
    password = CharField()
    
    class Meta:
        database = SqliteDatabase(DB_URI)
        table_name = 'credentials'
