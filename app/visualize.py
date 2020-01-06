from config import VISUAL_PATH
from db import engine, News, Sentiments, Scores
from matplotlib.pyplot import figure 
from os.path import abspath, dirname, join
from pandas import DataFrame, read_sql_table, Timedelta, to_datetime
from seaborn import barplot, lineplot
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker


def score():
    """
    Calculates daily aggregated sentiment ratio for news.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    max_scored_dt = session.query(func.max(Scores.dt)).scalar() or "2019-01-01"
    max_scored_dt = to_datetime(max_scored_dt) 
    max_scored_dt += Timedelta("1 day")
    max_scored_dt = max_scored_dt.isoformat()

    query = session.query(News.source.label("source"),  
                          News.etl_dttm.label("dt"),
                          Sentiments.sent_comparative.label("score"))\
                   .join(Sentiments, 
                         News.id == Sentiments.id)\
                   .filter(News.etl_dttm >= max_scored_dt)\
                   .all()
    data = DataFrame(query)
    if data.shape[0]:
        data["dt"] = data["dt"].apply(lambda x: x[:10])
        groupers = ["dt", "source"]
        data = data.groupby(groupers, as_index=False).mean()
        for item in data.to_dict('records'):
            session.add(Scores(**item))
            session.commit()


def plot_bars(dt=None):
    """
    Plots single score as boxplot for news sources.
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


if __name__ == "__main__":
    score()
    plot_bars()
    plot_lines()
    