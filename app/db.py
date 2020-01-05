from sqlalchemy import create_engine, Column, Integer, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from config import SQLALCHEMY_DATABASE_URI, DB_PATH
from sqlite3 import complete_statement, connect, Error
import logging
from os.path import abspath, dirname, join

engine = create_engine(SQLALCHEMY_DATABASE_URI)

Base = declarative_base()

class News(Base):
    __tablename__ = 'news'
    
    id = Column(Integer, primary_key = True)
    source = Column(Text)
    url = Column(Text)
    title = Column(Text) 
    description = Column(Text) 
    fulltext = Column(Text)
    authors = Column(Text) 
    keywords = Column(Text)
    rubric = Column(Text)
    pub_dttm = Column(Text) 
    etl_dttm = Column(Text)
    
    def __repr__(self):
        return "{} news: {}, {}".format(self.source, 
                                        self.title, 
                                        self.pub_dttm)

class Sentiments(Base):
    __tablename__ = 'sentiments'
    
    id = Column(Integer, primary_key = True)
    dost_negative = Column(Float)
    dost_neutral = Column(Float)
    dost_positive = Column(Float)
    dost_skip = Column(Float)
    dost_speech = Column(Float)
    sent_score = Column(Float)
    sent_positive = Column(Float)
    sent_negative = Column(Float)
    sent_comparative = Column(Float)

    def __repr__(self):
        return "sentiments for news id = {}".format(self.id)

logging.basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    filename = join(dirname(DB_PATH), "db.log")
)

def execute_query(query = "", *args):
    """
    Executes query to sqlite database.

    Params:
    query: text of sql query with one statement
    *args: placeholders for query 
           (additional arguments passed to cursor.execute method)
    """
    query = str(query)
    result = None
    err_msg_tmpl = "An error while executing query:\n" + \
                   "Error: {}\n" + \
                   "Query: " + query
    err_msg = ''
    if complete_statement(query):
        conn = connect(DB_PATH) 
        c = conn.cursor()
        try:
            c.execute(query, *args)
            if query.strip().lower().startswith('select'):
                result = c.fetchall()
            conn.commit()
        except Error as e:
                err_msg = err_msg_tmpl.format(e.args[0])
        finally:
            conn.close()
    else:
        err_msg = err_msg_tmpl.format('Incorrect query: not complete sql statement')
    if err_msg:
        logging.info(err_msg)
    return result


CREATE_QUERY_TMPL = "CREATE TABLE IF NOT EXISTS {table} ({columns});"
INSERT_QUERY_TMPL = "INSERT INTO {table} ({columns}) VALUES ({values});"

if __name__ == "__main__":
    Base.metadata.create_all(engine)