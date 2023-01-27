from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dogcat.db'
db = SQLAlchemy()

class User(db.Model): # пол и возраст пользователя (студент / не студент).
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    gender = db.Column(db.Text)
    age = db.Column(db.Integer)

class Answers(db.Model): # таблица с ответами пользователя на вопросы.
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key = True)
    q1 = db.Column(db.Text)
    q2 = db.Column(db.Text)
    q3 = db.Column(db.Text)
    q4 = db.Column(db.Text)
    q5 = db.Column(db.Text)

db.init_app(app) # коллабим.

@app.before_first_request # создаём базу данных...
def db_creation():
    db.create_all()

@app.route('/') 
@app.route('/main') # возврат на главную страницу...
def index():
    return render_template("base.html")

@app.route('/questions') # вопросы с помощью функции, на этой странице опрос.
def questions():
    return render_template(
        'questions.html'
    )

@app.route('/process', methods = ['get']) # тут сбор информации...
def answer_process():
    if not request.args:
        return redirect(url_for('questions'))
    
    gender = request.args.get('gender')
    age = request.args.get('age')
    
    user = User(
        age = age,
        gender = gender
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user) # подгрузка информации о пользователе в бд
    
    q1 = request.args.get('q1')
    q2 = request.args.get('q2')
    q3 = request.args.get('q3')
    q4 = request.args.get('q4')
    q5 = request.args.get('q5')

    answer = Answers(id = user.id, q1 = q1, q2 = q2, q3 = q3, q4 = q4, q5 = q5)
    db.session.add(answer)
    db.session.commit()
    
    return render_template("answer.html") 

@app.route('/results') # какие результаты + статистика по ответам.
def results():
    all = {}
    ageresults = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all['age_mean'] = ageresults[0] # средний возраст респондентов.
    all['age_min'] = ageresults[1] # самый младший респондент.
    all['age_max'] = ageresults[2] # самый старший респондент.
    all['total_count'] = User.query.count() # всего прошло опрос столько...

    return render_template('results.html', all = all)

if __name__ == "__main__":
    app.run()
