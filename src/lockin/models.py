from peewee import SqliteDatabase, CharField, Model, DateTimeField
from settings import DB_URI, NETWORK_DB_URI, TESTING_DB_URI


class Credentials(Model):
    service = CharField()
    username = CharField()
    password = CharField()

    class Meta:
        database = SqliteDatabase(DB_URI)
        table_name = "credentials"


class Connections(Model):
    timestamp = DateTimeField()

    class Meta:
        database = SqliteDatabase(DB_URI)
        table_name = "connections"


class NetCredentials(Model):
    service = CharField()
    username = CharField()
    password = CharField()

    class Meta:
        database = SqliteDatabase(NETWORK_DB_URI)
        table_name = "credentials"


class NetConnections(Model):
    timestamp = DateTimeField()

    class Meta:
        database = SqliteDatabase(NETWORK_DB_URI)
        table_name = "connections"


class TestCredentials(Model):
    service = CharField()
    username = CharField()
    password = CharField()

    class Meta:
        database = SqliteDatabase(TESTING_DB_URI)
        table_name = "credentials"


class TestConnections(Model):
    timestamp = DateTimeField()

    class Meta:
        database = SqliteDatabase(TESTING_DB_URI)
        table_name = "connections"
