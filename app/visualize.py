from matplotlib import pyplot as plt 
from db import engine, News, Sentiments
from config import PATH
from sqlalchemy.orm import sessionmaker
from numpy import mean

def score():
    """
    Calculates aggregated sentiment ratio for news.
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(News.source, 
                          News.etl_dttm, 
                          Sentiments.sent_comparative)\
                   .join(Sentiments, 
                         News.id == Sentiments.id)\
                   .limit(5)\
                   .all()
    return query

print(score())

def boxplot(scores_df):
    """
    Plots single score as boxplot for news sources.
    """
    pass

def lineplot(scores_df):
    """
    Plots scores in dynamic (one line for each score).
    """