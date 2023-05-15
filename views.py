from flask import Flask, render_template, url_for, redirect, request, session, flash
import sqlite3
from settings import key
import datetime
import random
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = key.gen()
app.config['MAIL_SERVER'] = 'smtp.mail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = '46az9jr3ir3m@mail.ru'  # введите свой адрес электронной почты здесь
app.config['MAIL_DEFAULT_SENDER'] = '46az9jr3ir3m@mail.ru'  # и здесь
app.config['MAIL_PASSWORD'] = 'LKnkcfNRkGDqxbTi95DL'  # введите пароль
mail = Mail(app)


def opendb():
    global db,cursor
    db = sqlite3.connect('db.sqlite3')
    cursor = db.cursor()

def closedb():
    cursor.close()
    db.close()

@app.route("/information")
def inform():
    opendb()
    query = 'select * from information'
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('information.html', result=result)

@app.route("/")
def index():
    if 'isLogged' not in session:
        return redirect('login')
    elif 'isLogged' in session:
        return redirect('home')


@app.route('/home')
def home():
    if 'isLogged' in session:
        opendb()
        query = 'select * from posts'
        cursor.execute(query)
        posts = cursor.fetchall()
        return render_template('index.html', posts=posts)
    else:
        return redirect('login')
    
@app.route("/login",methods=["GET","POST"])
def login():
    # Если со странице приходит запрос
    if request.method == "POST":
        # получаем данные из полей
        login = request.form.get('login')
        password = request.form.get('password')
        opendb()
        query_info = 'select * from users where login=(?) and password=(?)'
        cursor.execute(query_info, [login,password])
        # создадим объект пользователя
        user = cursor.fetchone()
        if user is not None: 
            session['isLogged'] = user[0]
            closedb()
            return redirect('/cabinet')
        else:
            flash('Ошибка авторизации, неверный логин или пароль')
    # Если страница просто открывается
    return render_template('login.html')
    
@app.route("/cabinet",methods=["GET","POST"])
def cabinet():
    if 'isLogged' in session:

    #@isLogin
    # Если со странице приходит запрос
        if request.method == "POST":
            # получаем данные из полей
            title = request.form.get('title')
            descr = request.form.get('descr')
            date = str(datetime.datetime.today().replace(microsecond=0))
            opendb()
            cursor.execute(f'INSERT INTO posts(id, title, descr, date) VALUES(?, ?, ?, ?)',[session['isLogged'], title, descr, date])
            db.commit()
            closedb()
            return redirect('/home')
        else:
            opendb()
            cursor.execute('select * from posts where id=(?)', [session['isLogged']])
            posts = cursor.fetchall()
            cursor.execute('select * from users_info where id=(?)', [session['isLogged']])
            user = cursor.fetchone()
            closedb()
        #print(session['isLogged'])
        return render_template('cabinet.html', posts=posts, user=user)
    else:
        return redirect('login')

@app.route("/logout")
def logout():
    del session['isLogged']
    return redirect('/login')

@app.route("/about_us")
def about_us():
    return render_template('about_us.html')

@app.route('/post/<int:post_id>', methods=['GET','POST'])
def showPost(post_id):
    if 'isLogged' in session:
        #return int(post_id)
        opendb()
        cursor.execute('select * from posts where post_id=(?)', [post_id])
        post = cursor.fetchone()
        #print(post)
        user_id = session['isLogged']
        closedb()
        return render_template('post.html', post=post, user_id=user_id)
    else:
        return redirect('login')

@app.route('/deletepost/<int:post_id>', methods=['GET','POST'])
def deletePost(post_id):
    #return int(post_id)
    opendb()
    cursor.execute('DELETE FROM posts WHERE post_id=(?)', [post_id])
    db.commit()
    closedb()
    return redirect('home')

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        session['isRegistor'] = {}
    # получаем данные из полей
        login = request.form.get('user_login')
        password = request.form.get('user_password')
        confirm_password = request.form.get('confirm_password')
        session['isRegistor']['login'] = request.form.get('login')
        session['isRegistor']['password'] = request.form.get('password')
        session['isRegistor']['email'] = request.form.get('email')
        session['isRegistor']['firstname'] = request.form.get('user_firstname')
        session['isRegistor']['lastname'] = request.form.get('user_lastname')
        session['isRegistor']['major'] = request.form.get('user_major')
        session['isRegistor']['age'] = request.form.get('user_age')
        session['isRegistor']['bdate'] = request.form.get('user_bdate')
        session['isRegistor']['sex'] = request.form.get('user_sex')
        session['isRegistor']['confirm_code'] = random.randint(100000,999999)
        opendb()
        cursor.execute('select * from users where login=(?)', [login])
        if cursor.fetchone() is None:
            if confirm_password == password:
                if int(session['isRegistor']['age']) >= 1 and int(session['isRegistor']['age']) <= 150:
                    try:
                        msg = Message('Код подтверждения:', recipients=[session['isRegistor']['email']])
                        msg.body = f'Код подтверждения: { session["isRegistor"]["confirm_email"]}'
                        mail.send(msg)
                        closedb()
                        return redirect('confirmemail')
                    except:
                        flash('Сервер временно недоступен')
                else:
                        flash('Возраст не коректен')
            else:
                    flash('Пароли не совпадают')
        else:
            flash('Такой логин уже используется')
        #return redirect('login')
    return render_template('register.html')


@app.route('/confirmemail', methods=["GET","POST"])
def registeremail():
    if request.method == "POST":
        confirm_email = request.form.get('confirm_code')
        if session['isRegistor']['confirm_code'] == str(confirm_email):
            try:
                cursor.execute(f'INSERT INTO users(login, password, email) VALUES(?, ?, ?)',[session['isRegistor']['login'], session['isRegistor']['password'], session['isRegistor']['email']])
                cursor.execute(f'INSERT INTO users_info(firstname, lastname, age, major, bdate, sex) VALUES(?, ?, ?, ?, ?, ?)',[session['isRegistor']['firstname'], session['isRegistor']['lastname'], session['isRegistor']['age'], session['isRegistor']['major'], session['isRegistor']['bdate'], session['isRegistor']['sex']])
                db.commit()
                closedb()
                del session['isRegistor']
                return redirect('confirmemail')
            except:
                flash('Ошибка регистрации')

    return render_template('confirmemail.html')

if __name__ == "__main__":
    app.run(debug=True)
