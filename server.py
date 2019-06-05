#!/usr/env/bin python3
import requests as req
from flask import Flask, Response, jsonify, request, views,json
import sqlite3

def dictfetch(cursor):
    data = cursor.fetchall()
    fields = [desc[0] for desc in cursor.description]
    result = [
        {key: value for key, value in zip(fields, item)}
        for item in data
    ]
    return result

def create_user(data):
    if data.get('UserId') is not None and data.get('FirstName') is not None and data.get('LastName') is not None:
        try:
            with sqlite3.connect('BDVKBot.db') as conn:
                c = conn.cursor()
                c.execute(
                    'INSERT INTO Users (UserId, FirstName, LastName) VALUES (?, ?,?)',
                    (data.get('UserId'),data.get('FirstName'), data.get('LastName')),
                )
                c.execute('SELECT * FROM Users WHERE UserId = (?)',(data.get('UserId'),))
                data = {dictfetch(c)}
                data['status'] = "Вы успешно зареганы"
        except sqlite3.IntegrityError:
            data = {"status":"Вы уже зареганы"}

    return data

def create_category(data):
    try:
        if data.get('UserId') is not None and data.get('NewsCategory') is not None:
            with sqlite3.connect('BDVKBot.db') as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO UsersCategory(NewsCategoryId,UserId) VALUES((SELECT NewsCategoryId FROM NewsCategory WHERE Name=(?)),(SELECT UserId FROM Users WHERE UserId=(?)))",
                (data.get('NewsCategory'),data.get('UserId'))
                )

                c.execute('SELECT * FROM UsersCategory WHERE UserId = (?)',(data.get('UserId'),))
                data = {"status":"Новая категория добавлена"}
    except sqlite3.IntegrityError:
        data = {"status":"Уже добавлено"}
    return data
def get_category(data):
    if data.get('UserId') is not None:
        with sqlite3.connect('BDVKBot.db') as conn:
            c = conn.cursor()
            c.execute("select Name from NewsCategory as NC left join UsersCategory as UC on NC.NewsCategoryId=UC.NewsCategoryId left join Users as U on U.UserId=UC.USerId where U.UserId = (?) order by U.UserId desc",
        (data.get('UserId'),))
            data ={"status":dictfetch(c)}
    if len(data) ==0:
        data = {"status":"Нет активных подписок"}

    return data
def delete_category(data):
    if data.get('UserId') is not None and data.get('NewsCategory') is not None:
        with sqlite3.connect('BDVKBot.db') as conn:
            c = conn.cursor()
            c.execute(
                "DELETE FROM UsersCategory WHERE (?) = (SELECT Name FROM NewsCategory WHERE NewsCategory.NewsCategoryId=UsersCategory .NewsCategoryId) AND UsersCategory.UserId = (?) ",
        (data.get('NewsCategory'), data.get('UserId')))

            c.execute(
                "select Name from NewsCategory as NC left join UsersCategory as UC on NC.NewsCategoryId=UC.NewsCategoryId left join Users as U on U.UserId=UC.USerId where U.UserId = (?) order by U.UserId desc",
                (data.get('UserId'),))
            data = {"status":"Удалено"}
            print(dictfetch(c))
    if len(data) == 0:
        data = {"status":"Нет активных подписок"}
    return data



def create_source(data):
    try:
        if data.get('UserId') is not None and data.get('KeyWord') is not None:
            with sqlite3.connect('BDVKBot.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO KeyWords(KeyWord) VALUES((?))",(data.get('KeyWord'), ))
                conn.commit()
                c.execute("INSERT INTO UserKeyWords(KeyWordsId,UserId) VALUES((SELECT KeyWordsId FROM KeyWords WHERE KeyWord=(?)),(SELECT UserId FROM Users WHERE UserId=(?)))",
             (data.get('KeyWord'), data.get('UserId')))
                conn.commit()
                c.execute('SELECT * FROM UserKeyWords WHERE UserId = (?)',(data.get('UserId'),))
                data = {"status":"Ключевое слово добавлено"}
    except sqlite3.IntegrityError:
        data = {"status":"Уже добавлено"}
    return data
def get_source(data):
    if data.get('UserId') is not None:
        with sqlite3.connect('BDVKBot.db') as conn:
            c = conn.cursor()
            c.execute("select KeyWord from KeyWords as KW left join UserKeyWords as UKW on KW.KeyWordsId=UKW.KeyWordsId left join Users as U on U.UserId=UKW.USerId where U.UserId = (?) order by U.UserId desc",
        (data.get('UserId'),))
            data ={"status":dictfetch(c)}
    if len(data) ==0:
        data = {"status":"Нет активных подписок"}

    return data
def delete_source(data):
    if data.get('UserId') is not None and data.get('KeyWord') is not None:
        with sqlite3.connect('BDVKBot.db') as conn:
            c = conn.cursor()
            c.execute(
                "DELETE FROM UserKeyWords WHERE  (?) = (SELECT KeyWord FROM KeyWords WHERE KeyWords.KeyWordsId=UserKeyWords.KeyWordsId)  AND UserKeyWords.UserId = (?) ",
            (data.get('KeyWord'), data.get('UserId')))

            c.execute(
                "select KeyWord from KeyWords as NC left join UserKeyWords as UC on NC.KeyWordsId=UC.KeyWordsId left join Users as U on U.UserId=UC.USerId where U.UserId = (?) order by U.UserId desc",
                (data.get('UserId'),))
            data = {"status":"Ключевое слово удален"}
            print(dictfetch(c))
    if len(data) == 0:
        data = {"status":"Нет активных подписок"}
    return data

def get_news_category(data):
    if data.get('UserId') is not None:
        with sqlite3.connect('BDVKBot.db') as conn:
            c = conn.cursor()
            c.execute("select Name from NewsCategory as NC left join UsersCategory as UC on NC.NewsCategoryId=UC.NewsCategoryId left join Users as U on U.UserId=UC.USerId where U.UserId = (?) order by U.UserId desc",
            (data.get('UserId'),))
            categories = c.fetchall()
            data = api_category(categories)
    if len(categories) ==0:
        data = {"status":"Нет активных подписок"}

    return data
def api_category(category,country='ru'):
    titles = []
    mas = []

    for item in category:
        text = ''.join(item)
        url = ('https://newsapi.org/v2/top-headlines?'
               f'country={country}&'
               f'category={text}&'
               'apiKey=6833f76c2dd3469a8a5bbe2d8741fbd5'
               )
        answr = json.loads(req.get(url).text)
        for i in answr['articles']:
            titles.append(i['title'])
            titles.append(i['url'])
            titles.append(i['urlToImage'])
            if len(titles) > 9:
                break

        for a in range(0,len(titles),3):
            date = {"title":titles[a],"url": titles[a+1],"pic": titles[a+2]}
            mas.append(date)

    return mas


def get_news_source(data):
    if data.get('UserId') is not None:
        with sqlite3.connect('BDVKBot.db') as conn:
            c = conn.cursor()
            c.execute("select KeyWord from KeyWords as KW left join UserKeyWords as UKW on KW.KeyWordsId=UKW.KeyWordsId left join Users as U on U.UserId=UKW.USerId where U.UserId = (?) order by U.UserId desc",
            (data.get('UserId'),))
            keywords = c.fetchall()
            data = {"status":api_source(keywords)}
    if len(keywords) ==0:
        data = {"status":"Нет активных подписок"}

    return data
def api_source(keywords,language='ru'):
    text = ''
    titles = []
    mas = []
    for item in keywords:

        text = text + ''.join(item) + '+'

    url = ('https://newsapi.org/v2/everything?'
           f'q={text}&'
           'sortBy=relevancy&'
           f'language={language}&'
           'apiKey=6833f76c2dd3469a8a5bbe2d8741fbd5'
           )
    answr = json.loads(req.get(url).text)
    for i in answr['articles']:
        titles.append(i['title'])
        titles.append(i['url'])
        titles.append(i['urlToImage'])
        if len(titles) > 30:
            break
    print(answr)
    for a in range(0, len(titles), 3):
        date = {"title": titles[a], "url": titles[a + 1], "pic": titles[a + 2]}
        mas.append(date)
    return mas

app = Flask(__name__)


@app.route('/')
def index():
    return Response('Hello, World!')


class UsersView(views.MethodView):
    def post(self):
        data = create_user(request.args)
        return jsonify(data)

class SubscriptionsView(views.MethodView):
    def post(self):
        data = create_category(request.args)
        return jsonify(data)
    def get(self):
        data = get_category(request.args)
        return jsonify(data)
    def delete(self):
        data = delete_category(request.args)
        return jsonify(data)

class CategoryView(views.MethodView):
    def post(self):
        data = create_source(request.args)
        return jsonify(data)
    def get(self):
        data = get_source(request.args)
        return jsonify(data)
    def delete(self):
        data = delete_source(request.args)
        return jsonify(data)

class NewsCategoryView(views.MethodView):
    def get(self):
        data = get_news_category(request.args)
        return jsonify(data)

class NewsKeywordsView(views.MethodView):
    def get(self):
        data = get_news_source(request.args)
        return jsonify(data)
app.add_url_rule('/users/', view_func=UsersView.as_view('users'))
app.add_url_rule('/subscriptions/categories/', view_func=SubscriptionsView.as_view('subscategory'))
app.add_url_rule('/subscriptions/keywords/', view_func=CategoryView.as_view('subssources'))
app.add_url_rule('/news/categories/', view_func=NewsCategoryView.as_view('newscategory'))
app.add_url_rule('/news/keywords/', view_func=NewsKeywordsView.as_view('newskeywords'))