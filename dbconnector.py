import logging
import sqlite3
from settings import DB_PATH, NEWS_TAB, NEWS_COLS

logging.basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    filename = "dbconnector.log"
)

def execute_query(query = "", *args):
    """
    Executes query to sqlite database.

    Params:
    query: text of sql query with one statement
    *args: placeholders for query (additional arguments passed to cursor.execute method)
    """
    query = str(query)
    result = None
    err_msg_tmpl = "An error while executing query:\n" + \
                   "Error: {}\n" + \
                   "Query: " + query
    err_msg = ''
    if sqlite3.complete_statement(query):
        conn = sqlite3.connect(DB_PATH) 
        c = conn.cursor()
        try:
            c.execute(query, *args)
            if query.strip().lower().startswith('select'):
                result = c.fetchall()
            conn.commit()
        except sqlite3.Error as e:
                err_msg = err_msg_tmpl.format(e.args[0])
        finally:
            conn.close()
    else:
        err_msg = err_msg_tmpl.format('Incorrect query: not complete sql statement')
    if err_msg:
        logging.info(err_msg)
    return result


if __name__ == "__main__":
    
    create_news_tab_query = "CREATE TABLE IF NOT EXISTS {tablename}\n({columns});".format(
        tablename = NEWS_TAB, 
        columns = ',\n'.join(
            map(
                lambda x: ' '.join(x), 
                NEWS_COLS.items()
            )
        )
    )

    execute_query(create_news_tab_query)