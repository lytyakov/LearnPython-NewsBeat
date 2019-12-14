DB_PATH =  "./news.db"

NEWS_TAB =  "news"

NEWS_COLS = {
    "id": "TEXT", 
    "title": "TEXT", 
    "description": "TEXT", 
    "fulltext": "TEXT", 
    "link": "TEXT", 
    "publication_dt": "TEXT", 
    "rss_etl_dt": "TEXT", 
    "text_rss_dt": "TEXT"
}

RSS_SOURCES = {
        "ria": "https://ria.ru/export/rss2/index.xml",
        "tass": "http://tass.ru/rss/v2.xml",
        "meduza": "https://meduza.io/rss/all",
        "newsru": "https://rss.newsru.com/all_news/"
}