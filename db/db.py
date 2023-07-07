from datetime import datetime

from peewee import PostgresqlDatabase, BigIntegerField, TextField, DateTimeField, Model, BigAutoField, BooleanField, \
    IntegerField

import conf

db = PostgresqlDatabase(None)


def init():
    config = conf.get()

    db.init(
        config["db"]["name"],
        user=config["db"]["user"],
        password=config["db"]["password"],
        host=config["db"]["host"],
        port=int(config["db"]["port"])
    )

    db.connect()

    db.create_tables([User])


def get() -> PostgresqlDatabase:
    return db


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = BigAutoField()
    chat_id = BigIntegerField()
    name = TextField()
    transaction_number = IntegerField(default=0)
    old_client = BooleanField(default=False)
    first_paid = DateTimeField(null=True)
    paid_at = DateTimeField(null=True)
    updated_at = DateTimeField(default=datetime.now())
    created_at = DateTimeField(default=datetime.now())
