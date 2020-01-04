from db import engine, News, Sentiments
from sqlalchemy.orm import sessionmaker
from sentimental import Sentimental
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from os.path import dirname, join

import logging

logging.basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    filename = join(dirname(__file__), "sentiments.log")
)

if __name__ == "__main__":

    Session = sessionmaker(bind=engine)
    session = Session()

    analyzed_news = session.query(Sentiments.id)
    news = session.query(News)\
                  .filter(News.id.notin_(analyzed_news))\
                  .all()

    dstvsk_model = FastTextSocialNetworkModel(tokenizer=RegexTokenizer())
    sntmntl_model = Sentimental()

    models = {}
    models["dost"] = dstvsk_model.predict
    models["sent"] = sntmntl_model.analyze

    for item in news:
        sentiment = {"id": item.id}
        fulltext = item.description
        if fulltext:
            for prefix, model in models.items():
                try:
                    if prefix == "dost":
                        result = model([fulltext])[0]
                    else:
                        result = model(fulltext)
                    result = {"_".join([prefix, k]): v for k, v in result.items()}
                    sentiment.update(result)
                except Exception as e:
                    err_msg = "An error while sentiment analysis/n"
                    err_msg += e.args[0]
                    logging.info(err_msg)

        session.add(Sentiments(**sentiment))
        session.commit()
