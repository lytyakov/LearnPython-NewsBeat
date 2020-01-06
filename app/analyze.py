from config import PATH
from db import engine, News, Sentiments
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from logging import basicConfig, INFO, info
from os.path import dirname, join
from sentimental import Sentimental
from sqlalchemy.orm import sessionmaker
from visualize import score, plot_bars, plot_lines

basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = INFO,
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
                result = {"_".join([prefix, k]): v 
                          for k, v in result.items()}
                sentiment.update(result)
            except Exception as e:
                err_msg_tmpl = "An error while sentiment analysis:/n{}/n/n{}"
                err_msg = err_msg_tmpl.format(e.args[0], text)
                info(err_msg)
    return sentiment

def get_news_to_analyze():
    """
    Returns list of news which have no sentiment scores yet. 
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    analyzed_news = session.query(Sentiments.id)
    news = session.query(News)\
                  .filter(News.id.notin_(analyzed_news))\
                  .all()
    return news


def news_sentiment_score(item):
    """
    Calculates sentiment scores for news item and adds to db.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    sentiment = {"id": item.id}
    fulltext = item.fulltext
    result = analyze(fulltext)
    sentiment.update(result)
    session.add(Sentiments(**sentiment))
    session.commit()


if __name__ == "__main__":

    news = get_news_to_analyze()

    for item in news:
        news_sentiment_score(item)
    
    score()
    plot_bars()
    plot_lines()