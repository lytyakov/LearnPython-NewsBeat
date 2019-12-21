DB_PATH =  "./news.db"

TABLES = {
    "rss": {
        "id": "TEXT", 
        "title": "TEXT", 
        "description": "TEXT", 
        "guid": "TEXT", 
        "pubdate": "TEXT", 
        "etl_dttm": "TEXT"
    },
    "news": {
        "id": "TEXT", 
        "fulltext": "TEXT", 
        "author": "TEXT",
        "etl_dttm": "TEXT"
    }
}

RELATIONS = [
    [
        {
            "table": "rss",
            "column": "id",
            "is_multiple": False
        },
        {
            "table": "news",
            "column": "id",
            "is_multiple": False
        }
    ]
]

RSS_SOURCES = [
    "https://ria.ru/export/rss2/index.xml",
    "http://tass.ru/rss/v2.xml",
    "https://meduza.io/rss/all",
    "https://rss.newsru.com/all_news/"
]
