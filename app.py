from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import *
from datetime import *

app = Flask(__name__)
app.secret_key = ",sf';lk,4[po6i2046-0lx,ztoit0-490=084630-2d"

db = SqliteDatabase('tourist.db', pragmas={
    'journal_mode': 'wal',
    'busy_timeout': 5000
})


class Users(Model):
    nickname = CharField(16)
    password = CharField()

    class Meta:
        database = db


class Diary(Model):
    title = CharField()
    text = TextField()
    author = ForeignKeyField(Users, backref="diaries")
    time = DateTimeField(default=datetime.now)
    favorite = BooleanField(default=False)
    done = BooleanField(default=False)
    
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
    completed = BooleanField(default=False)
    when_completed = DateField()

    class Meta:
        database = db

db.create_tables([Users, Diary, Budget, Achievement])

@app.route('/new_diary', methods=["GET"])
def new_diary_page():
    if session.get("nickname"):
        return render_template('edit.html', active_menu="diary")
    return redirect('/auth')

@app.route('/diary/<int:id>', methods=["GET"])
def diary_page(id):
    if session.get("nickname"):
        diary = Diary.get_or_none(Diary.id == id)
        if diary is None:
            flash("Такой страницы не существует.")
            return redirect("/")
        if diary.author.nickname != session.get("nickname"):
            return redirect("/")

        return render_template('edit.html', active_menu="diary", title=diary.title, text=diary.text)
    return redirect('/auth')

@app.route('/diary/<int:id>', methods=["POST"])
def edit_diary(id):
    if session.get("nickname"):
        diary = Diary.get(Diary.id == id)
        if diary.author != Users.get(Users.nickname == session.get("nickname")):
            flash("Ошибка. Вы не являетесь автором этой записи")
            return redirect("/")
        diary.title = request.form["title"]
        diary.text = request.form["text"]
        diary.time = datetime.now()
        diary.save()
        return redirect("/")

@app.route('/new_diary', methods=["POST"])
def new_diary():
    if session.get("nickname"):
        title = request.form["title"]
        text = request.form["text"]
        if len(text) == 0 or len(title) == 0:
            flash("Ошибка. Заполните все поля...")
            return redirect("/new_diary")
        try:
            author = Users.get(Users.nickname == session.get('nickname'))
        except:
            flash("Ошибка. Повторите позже...")
            return redirect("/new_diary")
        diary = Diary.create(
            title=title,
            text=text,
            author=author,
            time=datetime.now()
        )
        return redirect("/")
    return redirect('/auth')

@app.route('/done_diary/<int:id>')
def done_diary(id):
    if session.get("nickname"):
        diary = Diary.get(Diary.id == id)
        diary.done = not diary.done 
        diary.save()
        return redirect("/")
    return redirect('/auth')


@app.route('/')
def index_page():
    if session.get("nickname"):
        user = Users.get(Users.nickname == session.get("nickname"))
        return render_template('index.html', active_menu="diary", all_diary=user.diaries)
    return redirect('/auth')

@app.route('/calendar')
def calendar_page():
    if session.get("nickname"):
        return render_template('calendar.html', active_menu="calendar")
    return redirect('/auth')


@app.route('/map')
def map_page():
    if session.get("nickname"):
        return render_template('map.html', active_menu="map")
    return redirect('/auth')


@app.route('/goals')
def goals_page():
    if session.get("nickname"):
        user = Users.get(Users.nickname == session.get("nickname"))
        all_achievement = user.achievs
        return render_template('goals.html', active_menu="goals", all_achievement=all_achievement)
    return redirect('/auth')

@app.route('/new_achievement', methods=["GET"])
def new_achievement_page():
    if session.get("nickname"):
        return render_template('edit_goal.html', active_menu="goals")
    return redirect('/auth')


@app.route('/new_achievement', methods=["POST"])
def new_achievement():
    if session.get("nickname"):
        title = request.form["title"]
        description = request.form["description"]
        if len(description) == 0 or len(title) == 0:
            flash("Ошибка. Заполните все поля...")
            return redirect("/new_achievement")
        try:
            author = Users.get(Users.nickname == session.get('nickname'))
        except:
            flash("Ошибка. Повторите позже...")
            return redirect("/new_achievement")
        achievement = Achievement.create(
            title=title,
            description=description,
            author=author,
            when_completed = datetime.now()
        )
        return redirect("/goals")
    return redirect('/auth')


@app.route('/done_achievement/<int:id>')
def done_achievement(id):
    if session.get("nickname"):
        achievement = Achievement.get(Achievement.id == id)
        achievement.completed = not achievement.completed
        achievement.save()
        return redirect("/goals")
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