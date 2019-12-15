import logging
import sqlite3
from config import DB_PATH, TABLES

logging.basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    filename = "sqlquery.log"
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
    
    create_query_tmpl = "CREATE TABLE IF NOT EXISTS {tablename} ({columns});"
    
    for tab, cols in TABLES.items():
        create_query = create_query_tmpl.format(
            tablename = tab,
            columns = ', '.join(' '.join(i) for i in cols.items())
        )
        execute_query(create_query)
        logging.info(create_query)
