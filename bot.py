import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlite3 as lite
import requests

import json
categories = ["business", "entertainment", "general", "health", "science", "sports", "technology"]
def load_categories(categories):
    try:
        for item in categories:
            con = lite.connect('BDVKBot.db')
            cur = con.cursor()
            cur.execute("INSERT INTO NewsCategory(Name) VALUES (?)",(item,))
            con.commit()
    except lite.IntegrityError:
        pass
def registration(user_id):
    mas = vk.users.get(user_ids=user_id)

    answer =json.loads(requests.post(f"http://127.0.0.1:5000/users?UserId={mas[0]['id']}&FirstName={mas[0]['first_name']}&LastName={mas[0]['last_name']}").text)
    vk.messages.send(  # Отправляем сообщение
        user_id=user_id,
        random_id=get_random_id(),
        message=f'{answer["status"]}'
    )
def add_category(user_id,user_text):
    text = user_text[12:]
    text = str(text).replace(' ', '')
    answer = json.loads(requests.post(f'http://127.0.0.1:5000/subscriptions/categories?UserId={user_id}&NewsCategory={text}').text)
    print(answer)
    vk.messages.send(  # Отправляем сообщение
        user_id=user_id,
        random_id=get_random_id(),
        message=f"{answer['status']}"
    )

def del_category(user_id,user_text):
    text = user_text[12:]
    text = str(text).replace(' ', '')

    answer = json.loads(requests.delete(f'http://127.0.0.1:5000/subscriptions/categories?UserId={user_id}&NewsCategory={text}').text)
    vk.messages.send(  # Отправляем сообщение
        user_id=user_id,
        random_id=get_random_id(),
        message=f'{answer["status"]}'
    )
def view_category(user_id):
    answer = json.loads(requests.get(f'http://127.0.0.1:5000/subscriptions/categories?UserId={user_id}').text)
    vk.messages.send(  # Отправляем сообщение
        user_id=user_id,
        random_id=get_random_id(),
        message=f'{[i["Name"] for i in answer["status"]]}'
    )


def view_sources(user_id):
    answer = json.loads(requests.get(f'http://127.0.0.1:5000/subscriptions/keywords?UserId={user_id}').text)
    print(answer)
    vk.messages.send(  # Отправляем сообщение
        user_id=user_id,
        random_id=get_random_id(),
        message=f'{[i["KeyWord"] for i in answer]}'
    )

def add_source(user_id, user_text):
    text = user_text[10:]
    text = str(text).replace(' ', '')
    answer = json.loads(
        requests.post(f'http://127.0.0.1:5000/subscriptions/keywords?UserId={user_id}&KeyWord={text}').text)
    print(answer)
    vk.messages.send(  # Отправляем сообщение
        user_id=user_id,
        random_id=get_random_id(),
        message=f"{answer['status']}"
    )
def del_source(user_id, user_text):
    text = user_text[10:]
    text = str(text).replace(' ', '')
    answer = json.loads(
        requests.delete(f'http://127.0.0.1:5000/subscriptions/keywords?UserId={user_id}&KeyWord={text}').text)
    print(answer)
    vk.messages.send(  # Отправляем сообщение
        user_id=user_id,
        random_id=get_random_id(),
        message=f"{answer['status']}"
    )


def show_news_source(user_id):
    answer = json.loads(
        requests.get(f'http://127.0.0.1:5000/news/keywords?UserId={user_id}').text)
    print(answer)

    for i in answer['status']:
        vk.messages.send(  # Отправляем сообщение
            user_id=user_id,
            random_id=get_random_id(),
            message=f'Заголовок => {i["title"]}'
            f'\n URL => {i["url"]}'
            f'\n{i["pic"]}'
        )


def show_news_category(user_id):
    con = lite.connect('BDVKBot.db')
    cur = con.cursor()
    cur.execute(
        "select Name from NewsCategory as NC left join UsersCategory as UC on NC.NewsCategoryId=UC.NewsCategoryId left join Users as U on U.UserId=UC.USerId where U.UserId = (?) order by U.UserId desc",
        (user_id,))
    con.commit()
    categories = cur.fetchall()
    api_category(categories,user_id)

def api_category(category,user_id, country='ru'):
    for item in category:
        text = ''.join(item)
        url = ('https://newsapi.org/v2/top-headlines?'
               f'country={country}&'
               f'category={text}&'
               'apiKey=6833f76c2dd3469a8a5bbe2d8741fbd5'
               )
        responses = json.loads(requests.get(url).text)
        print(responses)
        push_news_category(responses, user_id)

def push_news_category(responsel,user_id):
    titles = []
    for i in responsel['articles']:
        titles.append(i['title'])
        titles.append(i['url'])
        titles.append(i['urlToImage'])
        if len(titles) > 9:
            break
    print(titles)
    for i in range(0, 9, 3):
        vk.messages.send(  # Отправляем сообщение
            user_id=user_id,
            random_id=get_random_id(),
            message=f'Заголовок => {titles[i]}'
            f'\n URL => {titles[i + 1]}'
            f'\n{titles[i + 2]}'
        )
def api_keywords(keywords,user_id,language = 'ru'):
    text = ''
    for item in keywords:
        text = text + ''.join(item) + '+'
    url = ('https://newsapi.org/v2/everything?'
           f'q={text}&'
           'sortBy=relevancy&'
           f'language={language}&'
           'apiKey=6833f76c2dd3469a8a5bbe2d8741fbd5'
           )
    response1 =json.loads(requests.get(url).text)
    push_news_keywords(response1,user_id)

def push_news_keywords(responsel,user_id):
    titles = []
    for i in responsel['articles']:
        titles.append(i['title'])
        titles.append(i['url'])
        titles.append(i['urlToImage'])
        if len(titles) > 30:
            break
    for i in range(0, 30, 3):
        vk.messages.send(  # Отправляем сообщение
            user_id=user_id,
            random_id=get_random_id(),
            message=f'Заголовок => {titles[i]}'
            f'\n URL => {titles[i + 1]}'
            f'\n{titles[i + 2]}'
        )




def read_messages():

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.text == '/info':
                vk.messages.send(  # Отправляем сообщение
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='/register - регистрация по id'
                            '\n /catigories - посмотреть доступные категории'
                            '\n /addcategory - добавить категорию'
                            '\n /delcategory - удалить категорию'
                            '\n /viewcategory - посмотреть категории'
                            '\n /addsource - добавить ключевые слова'
                            '\n /viewsources - посмотреть достпуные ключевые слова'
                            '\n /shownewssource - новости по ключевым словам'
                            '\n /shownewscategory - новости по категориям'

                )
            if event.text == '/register':
                registration(event.user_id)
            if event.text == '/categories':
                vk.messages.send(  # Отправляем сообщение
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message='доступные категории:'
                            '\n {}'.format(categories)

                )
            if '/addcategory' in event.text:
                add_category(event.user_id,event.text)
            if '/delcategory' in event.text:
                del_category(event.user_id,event.text)
            if event.text == '/viewcategory':
                view_category(event.user_id)
            if '/addsource' in event.text:
                add_source(event.user_id,event.text)
            if '/delsource' in event.text:
                del_source(event.user_id,event.text)
            if event.text == '/viewsources':
                view_sources(event.user_id)
            if event.text == '/shownewssource':
                show_news_source(event.user_id)
            if event.text == '/shownewscategory':
                show_news_category(event.user_id)



load_categories(categories)
vk_session = vk_api.VkApi(token='cfe1b45653e05a85fbdd478a0fa5f57daf467b76eaf9dcedc6ed1248563b2b52c8e063d2e3099c8f3a3e0')

longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()
read_messages()