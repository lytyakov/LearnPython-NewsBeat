import requests
import bs4
import logging
from config import PARSER_RULES
from datetime import datetime
from selenium import webdriver
from db import engine, News
from sqlalchemy.orm import sessionmaker

TEXTSEPARATOR = "\n"

logging.basicConfig(
    format = "%(asctime)s - %(levelname)s - %(message)s",
    level = logging.INFO,
    filename = "parser.log"
)

def parse_rss(source):
    """
    Returns generator of items in rss channel described in PARSER_RULES
    """
    source_url = PARSER_RULES[source]["url"]
    source_rss = PARSER_RULES[source]["rss"]
    try:
        rss_request = requests.get(source_url)
        rss_request.raise_for_status()
        rss_channel_tree = bs4.BeautifulSoup(rss_request.text, "html.parser")
    except (requests.RequestException, AttributeError, ValueError) as e:
        err_msg = "An error while getting rss channel:\n" + \
                  "Error: {}\n".format(e.args[0])
        logging.info(err_msg)
        yield None

    for item in rss_channel_tree.find_all('item'):
        result = {"source": source}
        for db_col, attr in source_rss.items():
            try:
                item_col_value = getattr(item, attr).get_text(strip=True)
            except AttributeError as e:
                item_col_value = None
                err_msg = "An error while parsing rss:\n" + \
                    "Error: {}\n".format(e.args[0]) + \
                    "Column: {}, attribute: {}\n".format(db_col, attr) + \
                    "Item: {}".format(item)
                logging.info(err_msg)
            finally:
                result[db_col] = item_col_value
        yield result
    

def parse_news(source, url):
    """
    Returns news item. Check PARSER_RULES for more info on parser rules
    """
    try:
        driver = webdriver.Safari()
        driver.get(url)
        page = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    except Exception as e:
        err_msg = "An error while getting news item:\n" + \
                  "Error: {}\n".format(e.args[0]) + \
                  "News: {}".format(url)
        logging.info(err_msg)
        return None
    finally:
        driver.close()
    
    source_news = PARSER_RULES[source]["news"]
    result = {}
    for attr, rule in source_news.items():
        try:
            tags = page.find_all(name=rule.get("tag"), 
                                 attrs=rule.get("attrs"))
            if "get" in rule:
                text = [tag.get(rule["get"]) for tag in tags]
            else:
                text = [tag.text for tag in tags]
            text = [t for t in text if isinstance(t, str)]
            result[attr] = TEXTSEPARATOR.join(text) 
        except Exception as e:
            err_msg = "An error while getting news item:\n" + \
                      "Error: {}\n".format(e.args[0]) + \
                      "News: {}".format(url)
            logging.info(err_msg)
            result[attr] = None
    result["etl_dttm"] = datetime.utcnow().isoformat()
    return result


if __name__ == "__main__":

    Session = sessionmaker(bind=engine)

    for source in PARSER_RULES:
        for item in parse_rss(source):
            session = Session()
            news_exists = session.query(News)\
                                 .filter(News.url == item["url"])\
                                 .count()
            if not news_exists:
                news = parse_news(source, item["url"])
                if news:
                    item.update(news)
                news = News(**item)
                session.add(news)
                session.commit()