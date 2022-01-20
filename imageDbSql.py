from peewee import *

db = MySQLDatabase('testdb', user='127.0.0.1', charset='utf8mb4')


class User(Model):
    """A base model that will use our MySQL database"""
    username = CharField()

    class Meta:
        database = db


db.connect()
db.create_tables([User])
