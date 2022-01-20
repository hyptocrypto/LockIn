from peewee import SqliteDatabase, CharField


class Credentials(Model):
    service = CharField()
    username = CharField()
    password = CharField()
    
    class Meta:
        database = SqliteDatabase("credentials.db")
        table_name = 'credentials'
