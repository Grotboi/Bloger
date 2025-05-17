import requests
from flask import Flask, redirect, render_template, request, url_for, session
import psycopg2
import random

app = Flask(__name__)
app.secret_key = 'MyV3ryS3cr3tK!3y_L0ngAndStr0ng'


@app.route("/")
def redic():
   
    return redirect("/index.html", code=302)
   
    
@app.route("/index.html")
def site():
      hid_url = "https://postman-echo.com/get"
      res = requests.get(hid_url)
      inter = res.json()
      headers = inter.get("headers", "No Simple")
      data = headers.get("host")
      connection = headers.get("connection")
      accept = headers.get("accept")
      return render_template("index.html", data = data, connection = connection, accept = accept)


@app.route("/main.html", methods=["POST"])
def test():
    test1 = request.form.get("name_input")
    post_data = {"input": test1}
    mysc = requests.post("https://postman-echo.com/post", data=post_data)
    return f"My opr: {post_data}"
   # return render_template("main.html", test1 = test1)

@app.route("/indexRegistr.html")
def reg_aout():
    return render_template("indexRegistr.html")
   
   
   
   # Регистрация/Авторизация
@app.route("/indexRegistr.html", methods=["GET","POST"])
def database():
    name = request.form.get("name")
    surname = request.form.get("surname")
    user_data = request.form.get("user_data")
    id_run = random.randint(1, 1000000)
    
    # Подключение к бд
    conn = psycopg2.connect(dbname="User_Blog", host="localhost", 
                           user="postgres", password="root", port="8887")
    cursor = conn.cursor()
    # Запись в бд
    cursor.execute("INSERT INTO user_reg_aut(id, name, surname, user_data) VALUES (%s, %s, %s, %s)", 
                  (f"@{id_run}", name, surname, user_data))
    conn.commit()
    cursor.close()
    conn.close()
    
    return render_template("indexRegistr.html")
    #return f"Data is: {name}, {surname}, {user_data}"




@app.route("/indexAuto.html", methods=["GET", "POST"])
def aut():
    error = None
    if request.method == "POST":
        autname = request.form.get("autname")
        autsurname = request.form.get("autsurname")

        # Подключение к БД
        conn = psycopg2.connect(dbname="User_Blog", host="localhost",
                                user="postgres", password="root", port="8887")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, surname FROM user_reg_aut WHERE name = %s AND surname = %s",
                       (autname, autsurname))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user'] = user[0]
            return redirect(url_for('indexPanel'))  
        else:
            error = "Неверное имя или фамилия"
    return render_template("indexAuto.html", error=error)
    
    
# Страница пользователя
@app.route("/indexPanel.html")
def indexPanel():
    if 'user' not in session:
        return redirect(url_for('aut'))
    
    username = session['user']
    
    conn = psycopg2.connect(dbname="User_Blog", host="localhost",
                                user="postgres", password="root", port="8887")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, surname FROM user_reg_aut WHERE id = %s",
                       (username,))
    user_data2 = cursor.fetchone()

    cursor.close()
    conn.close()
    
    return render_template("indexPanel.html", user=user_data2)    













if __name__ == "__main__":
    app.run(port=5000)














