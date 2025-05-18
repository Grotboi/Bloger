import os
import requests
from flask import Flask, redirect, render_template, request, url_for, session
import psycopg2
from urllib.parse import urlparse
import random

app = Flask(__name__)
app.secret_key = 'MyV3ryS3cr3tK!3y_L0ngAndStr0ng'

# Получаем DATABASE_URL из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL не установлена")

url = urlparse(DATABASE_URL)

@app.route("/")
def redic():
    return redirect(url_for("site"))

@app.route("/index.html")
def site():
    return render_template("index.html")

@app.route("/indexRegistr.html", methods=["GET", "POST"])
def database():
    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        user_data = request.form.get("user_data")
        password = request.form.get("password").strip()
        id_run = random.randint(1, 1000000)

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_reg_aut(id, name, surname, user_data, password) VALUES (%s, %s, %s, %s, %s)",
            (f"@{id_run}", name, surname, user_data, password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return render_template("indexRegistr.html")

    return render_template("indexRegistr.html")


@app.route("/indexAuto.html", methods=["GET", "POST"])
def aut():
    error = None
    if request.method == "POST":
        autname = request.form.get("autname")
        autsurname = request.form.get("autsurname")
        autpassword = request.form.get("autpassword")

        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, surname, password FROM user_reg_aut WHERE name = %s AND surname = %s",
                       (autname, autsurname))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user[3] == autpassword:
            session['user'] = user[0]
            return redirect(url_for('indexPanel'))
        else:
            error = "Неверное имя, фамилия или пароль"

    return render_template("indexAuto.html", error=error)


@app.route("/indexPanel.html", methods=["GET", "POST"])
def indexPanel():
    if 'user' not in session:
        return redirect(url_for('aut'))

    username = session['user']

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, surname FROM user_reg_aut WHERE id = %s", (username,))
    user_data2 = cursor.fetchone()

    if not user_data2:
        session.pop("user", None)
        return redirect(url_for('aut'))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        image_url = request.form.get("image_url")

        cursor.execute(
            "INSERT INTO posts(user_id, title, content, image_url) VALUES (%s, %s, %s, %s)",
            (username, title, content, image_url)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('indexPanel'))

    cursor.execute(
        "SELECT title, content, image_url FROM posts WHERE user_id = %s ORDER BY created_at DESC",
        (username,)
    )
    posts = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "indexPanel.html",
        user={
            "id": user_data2[0],
            "name": user_data2[1],
            "surname": user_data2[2]
        },
        posts=posts
    )


if __name__ == "__main__":
    app.run()