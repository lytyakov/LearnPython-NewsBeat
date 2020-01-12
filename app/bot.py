from config import PATH
from datetime import date
from db import engine, Chats
from json import loads
from os.path import join
from sqlalchemy.orm import sessionmaker
from telebot import TeleBot
from requests import post

with open(join(PATH, "credentials.json"), 'r') as f:
    TOKEN = loads(f.read())["TG_BOT_API_KEY"]

API_URL = "https://api.telegram.org/bot{token}/{method_name}"


def get_subscribed_chats():
    """
    Yields chat_id of subscribed chats.
    """
    today = date.today().isoformat()
    Session = sessionmaker(bind=engine)
    session = Session()
    chats = session.query(Chats)\
                   .filter(Chats.subscr_from <= today)\
                   .filter(Chats.subscr_to.is_(None))\
                   .all()
    for chat in chats:
        yield chat.chat_id


def send_plot(chat_id, plot):
    """
    Sends plot to chat_id.
    """
    method_name = "sendPhoto"
    url = API_URL.format(token=TOKEN, 
                         method_name=method_name)
    data = {"chat_id": chat_id}
    files = {"photo": plot}
    post(url, data=data, files=files)


tb = TeleBot(TOKEN)

@tb.message_handler(commands=['start', 'subscribe'])
def subscribe(message):
        
        chat_id = message.chat.id
        Session = sessionmaker(bind=engine)
        session = Session()
        subscribed = session.query(Chats)\
                            .filter(Chats.chat_id == chat_id)\
                            .filter(Chats.subscr_to.is_(None))\
                            .count()
        if subscribed:
            reply = "You're already subscribed."
        else:
            reply = "You have subscribed for LearnPython-NewsBeat."
            chat = {
                "chat_id": chat_id,
                "subscr_from": date.today().isoformat()
            }
            session.add(Chats(**chat))
            session.commit()
        reply += " To unsubscribe use /unsubscribe command"
        tb.reply_to(message, reply)


@tb.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
        
        chat_id = message.chat.id
        Session = sessionmaker(bind=engine)
        session = Session()
        subscribed = session.query(Chats)\
                            .filter(Chats.chat_id == chat_id)\
                            .filter(Chats.subscr_to.is_(None))\
                            .count()
        if subscribed:
            reply = "You have unsubscribed from LearnPython-NewsBeat."
            today = date.today().isoformat()
            session.query(Chats)\
                            .filter(Chats.chat_id == chat_id)\
                            .filter(Chats.subscr_to.is_(None))\
                            .update({Chats.subscr_to: today})
            session.commit()
        else:
            reply = "You are not subscribed!"
        tb.reply_to(message, reply)


if __name__ == "__main__":
    print("The bot is polling.")
    print("Press Control + C to stop polling.")
    tb.polling() 
