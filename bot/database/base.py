from peewee import SqliteDatabase, Model

db = SqliteDatabase("bot/database/database.db")


class BaseModel(Model):
    class Meta:
        database = db
