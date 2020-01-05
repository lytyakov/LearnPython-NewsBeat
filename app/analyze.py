from db import engine, News, Sentiments
from config import PATH
from sqlalchemy.orm import sessionmaker
from sentimental import Sentimental
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from os.path import dirname, join

import logging

logging.basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    filename = join(PATH, "sentiments.log")
)

MODELS = {}
MODELS["dost"] = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())
MODELS["sent"] = Sentimental()

def analyze(text):
    """
    Returns dict with predicted sentiment scores.
    Model name is used as a prefix of a score name.
    """
    sentiment = {}
    if text:
        for prefix, model in MODELS.items():
            try:
                if prefix == "dost":
                    result = model.predict([text])[0]
                elif prefix == "sent":
                    result = model.analyze(text)
                result = {"_".join([prefix, k]): v for k, v in result.items()}
                sentiment.update(result)
            except Exception as e:
                err_msg_tmpl = "An error while sentiment analysis:/n{}/n/n{}"
                err_msg = err_msg_tmpl.format(e.args[0], text)
                logging.info(err_msg)
    return sentiment


if __name__ == "__main__":

    Session = sessionmaker(bind=engine)
    session = Session()
    analyzed_news = session.query(Sentiments.id)
    news = session.query(News)\
                  .filter(News.id.notin_(analyzed_news))\
                  .all()

    for item in news:
        sentiment = {"id": item.id}
        fulltext = item.fulltext
        result = analyze(fulltext)
        sentiment.update(result)
        session.add(Sentiments(**sentiment))
        session.commit()