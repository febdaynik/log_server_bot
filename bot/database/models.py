import datetime

from peewee import CharField, IntegerField, DateTimeField, ForeignKeyField, IPField

from .base import BaseModel, db


class User(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = IntegerField(unique=True)
    username = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)


class Server(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField()
    owner = ForeignKeyField(User, field="user_id")
    ip_address = IPField()
    ssh_key = CharField()
    username = CharField(default="root")
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)


class ServerAccess(BaseModel):
    user = ForeignKeyField(User, field="user_id")
    server = ForeignKeyField(Server, field="id")


def init_db():
    db.connect()
    db.create_tables([User, Server, ServerAccess])
