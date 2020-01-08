from config import VISUAL_PATH
from datetime import date
from db import engine, Chats, News, Sentiments, Scores
from json import loads
from matplotlib.pyplot import figure 
from os.path import abspath, dirname, join
from pandas import DataFrame, read_sql_table
from seaborn import barplot, lineplot
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from telebot import TeleBot
from requests import post

with open("./app/credentials.json", 'r') as f:
    TOKEN = loads(f.read())["TG_BOT_API_KEY"]

API_URL = "https://api.telegram.org/bot{token}/{method_name}"

def get_chat_id():
    Session = sessionmaker(bind=engine)
    session = Session()
    chats = session.query(Chats).all()
    for chat in chats:
        yield chat.chat_id

def send_plot(chat_id, plot):
    method_name = "sendPhoto"
    url = API_URL.format(token=TOKEN, 
                         method_name=method_name)
    data = {"chat_id": chat_id}
    files = {"plot": plot}
    post(url, data=data, files=files)

tb = TeleBot(TOKEN)

@tb.message_handler(commands=['start', 'subscribe'])
def subscribe(message):
        reply = "You have subscribed for LearnPython-NewsBeat. "
        reply += "To unsubscribe use /unsubscribe command"
        chat_id = message.chat.id
        Session = sessionmaker(bind=engine)
        session = Session()
        chat = {
            "chat_id": chat_id,
            "subscr_from": date.today().isoformat()
        }
        session.add(Chats(**chat))
        session.commit()
        tb.reply_to(message, reply)

@tb.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
        reply = "You have unsubscribed from LearnPython-NewsBeat."
        tb.reply_to(message, reply)

if __name__ == "__main__":
    tb.polling() 