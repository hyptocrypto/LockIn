"""
Delete list of service. Useful for forgot passwords.
"""

from peewee import CharField, Model, SqliteDatabase

db = SqliteDatabase("../../julian_credentials.db")


class Credentials(Model):
    service = CharField()
    username = CharField()
    password = CharField()

    class Meta:
        database = db
        table_name = "credentials"


db.connect()

service_names = ["test", "test_service", "testtest"]
formatted_service_names = ", ".join(f"'{name}'" for name in service_names)

db.execute_sql(f"DELETE FROM credentials WHERE service IN ({formatted_service_names});")
db.close()
