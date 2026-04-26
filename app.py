from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import *

app = Flask(__name__)
app.secret_key = ",sf';lk,4[po6i2046-0lx,ztoit0-490=084630-2d"

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


@app.route('/')
def index_page():
    if session.get("nickname"):
        return render_template('index.html', active_menu="diary")
    return redirect('/auth')

@app.route('/calendar')
def calendar_page():
    if session.get("nickname"):
        return render_template('calendar.html', active_menu="calendar")
    return redirect('/auth')

@app.route("/registration")
def registration_page():
    if session.get("nickname"):
        return redirect("/")
    return render_template("registration.html")

@app.route("/registration", methods=["POST"])
def registration():
    nickname = request.form["nickname"]
    password = request.form["password"]
    password_r = request.form["password_r"]

    if password != password_r:
        flash("Пароли не совпадают")
        return redirect("/registration")
    
    if Users.select().where(Users.nickname == nickname).exists():
        flash("Такой логин уже существует")
        return redirect("/registration")
    
    try:
        password = generate_password_hash(password)
        user = Users.create(
            nickname=nickname,
            password=password,
        )
        session["nickname"] = user.nickname
        return redirect("/")
    except:
        flash("Ошибка сервера")
        return redirect("/registration")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/auth")
def auth_page():
    if session.get("nickname"):
        return redirect("/")
    return render_template("auth.html")

@app.route("/auth", methods=["POST"])
def authentication():
    nickname = request.form["nickname"]
    password = request.form["password"]

    try:
        user = Users.get(Users.nickname == nickname)
    except:
        flash("Такой никнейм не зарегистрирован")
        return redirect("/auth")
    
    if check_password_hash(user.password, password):
        session["nickname"] = user.nickname
        return redirect("/")
    else:
        flash("Неверный пароль")
        return redirect("/auth")


if __name__ == "__main__":
    app.run(debug=True)