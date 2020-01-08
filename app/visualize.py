from config import VISUAL_PATH
from db import engine, News, Sentiments, Scores
from json import loads
from matplotlib.pyplot import figure 
from os.path import abspath, dirname, join
from pandas import DataFrame, read_sql_table
from seaborn import barplot, lineplot
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from telebot import TeleBot


def plot_bars(dt=None):
    """
    Plots single score as barplot for news sources.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    if not dt:
        dt = session.query(func.max(Scores.dt)).scalar()
    query = session.query(Scores.source.label("source"),
                          Scores.score.label("score"))\
                   .filter(Scores.dt == dt)\
                   .all()
    data = DataFrame(query)

    fig = figure(figsize=(10,8))
    ax = fig.gca()
    barplot(
        x="score",
        y="source",
        data=data,
        ax=ax
    )
    filename = "barplot_{}.png".format(dt)
    filename = join(VISUAL_PATH, filename)
    fig.savefig(filename)


def plot_lines(start_dt=None, end_dt=None):
    """
    Plots scores in dynamic (one line for each source).
    """
    data = read_sql_table('scores', con=engine)
    if start_dt:
        data = data[data.dt.ge(start_dt)]
    if end_dt:
        data = data[data.dt.le(end_dt)]

    fig = figure(figsize=(10,8))
    ax = fig.gca()
    lineplot(
        x="dt",
        y="score",
        hue="source",
        data=data,
        ax=ax
    )
    filename = "lineplot_{}_{}.png".format(data.dt.min(), data.dt.max())
    filename = join(VISUAL_PATH, filename)
    fig.savefig(filename)


def plot_to_send():
    filename = "lineplot_2019-12-28_2020-01-05.png"
    return join(VISUAL_PATH, filename)
    

if __name__ == "__main__":
    plot_bars()
    plot_lines()
    