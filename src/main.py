from flask import Flask, render_template, redirect, url_for, session
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import func
from requests import Session
from flask.helpers import make_response
from datetime import datetime, timedelta
import jwt
import json
# For article summary
import nltk
from newspaper import Article
# For news extract
import requests

app = Flask(__name__)
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123321@localhost/Assignment4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'

db = SQLAlchemy(app)
db.init_app(app)

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '54027113-f309-4184-8950-3d1f53aca5dd'
}

get_id_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
get_news_url = 'https://api.coinmarketcap.com/content/v3/news?coins='

nltk.download('punkt')


session = Session()
session.headers.update(headers)


class Coin(db.Model):
    __tablename__ = 'Coin'
    id = db.Column('id', db.Integer, primary_key=True)
    coin_name = db.Column('coin_name', db.Unicode)

    def __init__(self, id, coin_name):
        self.id = id,
        self.coin_name = coin_name


class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column('id', db.Integer, primary_key=True)
    login = db.Column('login', db.Unicode)
    password = db.Column('password', db.Unicode)
    token = db.Column('token', db.Unicode)

    def __init__(self, id, login, password, token):
        self.id = id
        self.login = login
        self.password = password
        self.token = token

    def __repr__(self):
        return '<"id": %r,"login": "%r","password": "%r","token": "%r">' % (
        self.id, self.login, self.password, self.token)


class Articles(db.Model):
    __tablename__ = 'Articles'
    article_id = db.Column('article_id', db.Integer, primary_key=True, autoincrement=True)
    article_text = db.Column('article_text', db.UnicodeText)
    coin_id = db.Column('coin_id', db.Integer)

    def __init__(self, article_id, article_text, coin_id):
        self.article_id = article_id,
        self.article_text = article_text,
        self.coin_id = coin_id


def get_coin_id(coin):
    parameters = {
        'slug': coin
    }
    response = session.get(get_id_url, params=parameters)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return None
    for x in json.loads(response.content)['data']:
        id = json.loads(response.content)['data'][x]['id']
    return id


def get_coin_news(coin_id):
    page = requests.get(get_news_url + str(coin_id))
    urls = []
    for url in json.loads(page.content)['data']:
        urls.append(url['meta']['sourceUrl'])
    return urls


def get_coin_article(coin_news_url):
    article = Article(coin_news_url)
    article.download()
    try:
        article.parse()
    except:
        return None
    article.nlp()
    return article.summary


@app.route('/', methods=['GET', 'POST'])
def test():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('login'))
    return render_template('login.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print('im in post')
        row = Users.query.filter_by(login=request.form['username'],
                                    password=request.form['password']).first()

        if row is not None:
            token = jwt.encode(
                {'user': request.form['username'], 'pass': request.form['password'], 'exp': datetime.utcnow() +
                                                                                            timedelta(minutes=30)},
                app.config['SECRET_KEY'])
            if row.token != token or row.token == 'Null':
                row.token = token
                db.session.commit()
                token = row.token
            return redirect(url_for('form', token=token))
        else:
            print('im in error page')
            return render_template('login.html', error='User not found')
    else:
        print('im in get')
        return render_template('login.html', error=error)


@app.route('/coin', methods=['GET', 'POST'])
def form():
    token = request.args.get('token')
    row = Users.query.filter_by(token=token).first()
    if row is not None:
        if request.method == "POST":
            coin = request.form['coin']
            coin_id = get_coin_id(coin.lower())
            if coin_id is not None:
                row = Coin.query.filter_by(id=coin_id).first()
                if row is None:
                    new_coin = Coin(coin_id, coin)
                    db.session.add(new_coin)
                    db.session.commit()
                coin_news = get_coin_news(coin_id)
                articles = []
                for coin_news_url in coin_news:
                    article = get_coin_article(coin_news_url)
                    if article is None or article == 'Javascript is DisabledYour current browser configurationis not compatible with this site.':
                        continue
                    row = Articles.query.filter_by(article_text=article).first()
                    if row is None:
                        max_id = db.session.query(func.max(Articles.article_id)).scalar()
                        if max_id is None:
                            new_article = Articles(1, article, coin_id)
                        else:
                            new_article = Articles(max_id + 1, article, coin_id)
                        db.session.add(new_article)
                        db.session.commit()
                    articles.append(article)
                return render_template('coin.html', error=None, articles=articles)
            else:
                return render_template('coin.html', error='Coin not found')
        else:
            return render_template('coin.html', error=None)
    else:
        return make_response('Could not verify! Provided token is incorrect', 401)


if __name__ == '__main__':
    app.run(debug=True)
