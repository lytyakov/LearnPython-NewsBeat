import requests
import bs4
import hashlib
import logging
from sqlquery import execute_query
from config import DB_PATH, TABLES, RSS_SOURCES
import datetime

logging.basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    filename = "newsparser.log"
)

def parse_rss(url):
    """
    Returns generator of items in rss channel found at url
    """
    r = requests.get(url)
    etl_dttm = datetime.datetime.utcnow().isoformat()
    rss = bs4.BeautifulSoup(r.text, "html.parser")
    for item in rss.find_all('item'):
        result = dict().fromkeys(TABLES["rss"].keys())
        try:
            _id = hashlib.md5()
            for at in result:
                attr = getattr(item, at)
                if isinstance(attr, bs4.element.Tag):
                    attr = attr.get_text(strip = True)
                    result[at] = attr
                    _id.update(attr.encode('utf-8'))
            result['id'] = _id.hexdigest()
            result['etl_dttm'] = etl_dttm
            yield result
        except AttributeError as e:
            err_msg = "An error while parsing rss:\n" + \
                      "Error: {}\n".format(e.args[0]) + \
                      "Item: {}".format(item)
            logging.info(err_msg)


def parse_news(url):

    return


if __name__ == "__main__":

    insert_query_tmpl = "INSERT INTO {table} ({columns}) VALUES ({values});"

    for url in RSS_SOURCES:
        for item in parse_rss(url):
            execute_query(
                insert_query_tmpl.format(
                    table = "rss",
                    columns = ','.join(sorted(item.keys())),
                    values = ','.join(map(lambda x: ':'+x, sorted(item.keys())))
                ),
                item
            )
