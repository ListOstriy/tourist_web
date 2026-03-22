from flask import Flask, render_template
from peewee import *

app = Flask(__name__)
db = SqliteDatabase('tourist.db')

class Users(Model):
    nickname = CharField(16)
    password = CharField()


    class Meta:
        database = db


class Diary(Model):
    title = CharField()
    text = CharField()
    author = ForeignKeyField(Users, backref="diaries")
    time = DateTimeField()
    favorite = BooleanField()
    done = BooleanField()
    
    class Meta:
        database = db


class Budget(Model):
    name = CharField()
    price = FloatField()
    diary = ForeignKeyField(Diary, backref="budget")

    class Meta:
        database = db


class Achievement(Model):
    author = ForeignKeyField(Users, backref="achievs")
    title = CharField()
    description = CharField()
    completed = BooleanField()
    when_completed = DateField()

    class Meta:
        database = db

db.create_tables([Users, Diary, Budget, Achievement])

@app.route("/")
def index_page():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()