from bot import get_subscribed_chats, send_plot
from config import PATH, VISUAL_PATH
from datetime import date
from db import engine, News, Scores, Sentiments
from dostoevsky.models import FastTextSocialNetworkModel
from dostoevsky.tokenization import RegexTokenizer
from logging import basicConfig, INFO, info
from matplotlib.pyplot import figure, style
from os.path import dirname, join
from pandas import DataFrame, read_sql_table, Timedelta, to_datetime
from seaborn import despine, lineplot, set_style
from sentimental import Sentimental
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

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


def source_daily_score():
    """
    Calculates daily aggregated sentiment ratio for news.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    max_scored_dt = session.query(func.max(Scores.dt)).scalar() or "2019-01-01"
    max_scored_dt = to_datetime(max_scored_dt) 
    max_scored_dt += Timedelta("1 day")
    max_scored_dt = max_scored_dt.isoformat()
    
    today = to_datetime(date.today()).isoformat()

    query = session.query(News.source.label("source"),  
                          News.etl_dttm.label("dt"),
                          Sentiments.sent_comparative.label("score"))\
                   .join(Sentiments, 
                         News.id == Sentiments.id)\
                   .filter(News.etl_dttm >= max_scored_dt)\
                   .filter(News.etl_dttm < today)\
                   .all()
    data = DataFrame(query)
    if data.shape[0]:
        data["dt"] = data["dt"].apply(lambda x: x[:10])
        groupers = ["dt", "source"]
        data = data.groupby(groupers, as_index=False).mean()
        for item in data.to_dict('records'):
            session.add(Scores(**item))
            session.commit()


def plot_lines():
    """
    Plots scores in dynamic (one line for each source).
    """
    data = read_sql_table("scores", con=engine)
    
    style.use('seaborn-whitegrid')
    set_style("white")

    fig = figure(figsize=(12,8))
    ax = fig.gca()
    g = lineplot(
        x="dt",
        y="score",
        hue="source",
        data=data,
        palette="muted",
        markers=True,
        style="source",
        ax=ax
    )
    g.legend_.texts[0].set_text("")
    despine()
    ax.set(xlabel="", ylabel="")
    dt = data.dt.max().split("-")[::-1]
    fig.suptitle("Степень \"негативности\" новостей yа {}.{}.{}".format(*dt), 
                 fontsize=16)
    filename = "{}.png".format(data.dt.max())
    filename = join(VISUAL_PATH, filename)
    fig.savefig(filename)
    return filename


if __name__ == "__main__":

    news = get_news_to_analyze()
    for item in news:
        news_sentiment_score(item)
    source_daily_score()
    plot_to_send = plot_lines()
    chat_ids = get_subscribed_chats()
    with open(plot_to_send, "rb") as plot:
        for chat_id in chat_ids:
            send_plot(chat_id, plot)
