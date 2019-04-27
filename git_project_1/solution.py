from add_news import AddNewsForm
from redact_news import RedactNewsForm
from db import DB
from flask import Flask, redirect, render_template, session
from login_form import LoginForm
from news_model import NewsModel
from user_model import UsersModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db = DB()
NewsModel(db.get_connection()).init_table()
UsersModel(db.get_connection()).init_table()
admin_model = UsersModel(db.get_connection())
existss = admin_model.exists('admin', 'admin')
if not (existss[0]):
    admin_model.insert('admin', 'admin', 'admin')


# http://127.0.0.1:8080/login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
        return redirect("/index")
    return render_template('login.html', title='Авторизация', form=form)

# http://127.0.0.1:8080/reg
@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        user_model.insert(user_name, password, 'user')
        exists = user_model.exists(user_name, password)
        session['username'] = user_name
        session['user_id'] = exists[1]            
        return redirect("/index")
    return render_template('reg.html', title='Регистрация', form=form)

@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/login')
    news = NewsModel(db.get_connection()).get_all(session['user_id'])
    news.sort(key=lambda x: (x[4], x[1]))
    u_role = False
    role = UsersModel(db.get_connection()).get(session['user_id'])[3]
    if role == 'admin':
        u_role = True    
    return render_template('index.html', username=session['username'], news=news, users_link = u_role)

@app.route('/users')
def users():
    if 'username' not in session:
        return redirect('/login')
    role = UsersModel(db.get_connection()).get(session['user_id'])[3]
    if role != 'admin':
        return redirect('/index')
    all_user = UsersModel(db.get_connection()).get_all()
    users = []
    for user in all_user:
        users.append([user[1], len(NewsModel(db.get_connection()).get_all(user[0]))])
    return render_template('users.html', username=session['username'], users=users)


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if 'username' not in session:
        return redirect('/login')
    form = AddNewsForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        nm = NewsModel(db.get_connection())
        nm.insert(title, content, session['user_id'])
        return redirect("/index")
    return render_template('add_news.html', title='Добавление новости', form=form, username=session['username'])


@app.route('/delete_news/<int:news_id>', methods=['GET'])
def delete_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    nm = NewsModel(db.get_connection())
    nm.delete(news_id)
    return redirect("/index")



@app.route('/redact_news/<int:news_id>', methods=['GET', 'POST'])
def redact_news(news_id):
    if 'username' not in session:
        return redirect('/login')
    form = RedactNewsForm()
    nm = NewsModel(db.get_connection())
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        nm.insert(title, content, session['user_id'])
        nm.delete(news_id)
        return redirect("/index")
    form.title.data=nm.get(news_id)[1]
    form.content.data = nm.get(news_id)[2]
    return render_template('redact_news.html', form=form, username=session['username'])


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')