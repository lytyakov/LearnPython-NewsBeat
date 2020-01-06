import os

PATH = os.path.dirname(os.path.abspath(__file__))

DB_PATH =  os.path.join(PATH, "db", "news.db")
SQLALCHEMY_DATABASE_URI = "sqlite:///" + DB_PATH

VISUAL_PATH = os.path.join(PATH, "visual")

PARSER_RULES = {
    "ria": {
        "url": "https://ria.ru/export/rss2/index.xml",
        "rss": {
            "title": "title", 
            "description": "description", 
            "url": "guid", 
            "pub_dttm": "pubdate",
        },
        "news": {
            "fulltext": {
                "tag": "div",
                "attrs": {
                    "class": "article__text"
                } 
            },
            "authors": {
                "tag": "div",
                "attrs": {
                    "class": "article__author-name"
                }
            },
            "keywords": {
                "tag": "a",
                "attrs": {
                    "class": "article__tags-item"
                },
            },
            "rubric": {
                "tag": "meta",
                "attrs": {
                    "name": "analytics:rubric"
                },
                "get": "content"
            }
        }
    },
    "tass": {
        "url": "http://tass.ru/rss/v2.xml",
        "rss": {
            "title": "title", 
            "description": "description", 
            "url": "guid", 
            "pub_dttm": "pubdate",
        },
        "news": {
            "fulltext": {
                "tag": "p"
            },
            "authors": {
                "tag": "div",
                "attrs": {
                    "class": "person-name"
                } 
            },
            "keywords": {
                "tag": "a",
                "attrs": {
                    "class": "tags__item"
                }
            }
        }
    },
    "meduza": {
        "url": "https://meduza.io/rss/all",
        "rss": {
            "title": "title", 
            "description": "description", 
            "url": "guid", 
            "pub_dttm": "pubdate",
        },
        "news": {
            "fulltext": {
                "tag": "p",
                "attrs": {"class": "SimpleBlock-p"}
            },
            "authors": {
                "tag": "p",
                "attrs": {"class": "MaterialNote-note_caption"}
            },
            "keywords": {
                "tag": "meta",
                "attrs": {"name": "keywords"},
                "get": "content"
            },
            "rubric": {
                "tag": "div",
                "attrs": {
                    "class": "Tag-root Tag-large Tag-gold"
                }
            }
        }
    },
    "newsru": {
        "url": "https://rss.newsru.com/all_news/",
        "rss": {
            "title": "title", 
            "description": "description", 
            "url": "guid", 
            "pub_dttm": "pubdate",
        },
        "news": {
            "fulltext": {
                "tag": "p",
                "attrs": {
                    "class": "maintext"
                }
            },
            "authors": {
                "tag": "a",
                "attrs": {
                    "class": "article-author"
                }
            },
            "keywords": {
                "tag": "meta",
                "attrs": {
                    "name": "news_keywords"
                },
                "get": "content"
            },
            "rubric": {
                "tag": "div",
                "attrs": {
                    "class": "main-caption"
                }
            }
        }
    }
}