import json
import os, os.path
from datetime import datetime, timedelta
from time import sleep
from NewsAPI import GetGoogleArticles
from whoosh import index
from whoosh.fields import SchemaClass, TEXT, ID, DATETIME
from whoosh.analysis import StemmingAnalyzer
from whoosh.writing import AsyncWriter

JSON_RECORD = True

ARTICLE_INDEX_NAME = "articleIndex"
SCRAPE_TOPIC = "Coronavirus" # Follows Google search format
SCRAPE_START_DATE = '01/01/2020' # When to start scraping from
SCRAPE_PERIOD = 1 # How many days to scrape at once
SCRAPE_DELAY = 30 # Delay between scrapes in seconds
SCRAPE_PAGES = 3 # Amount of pages to use per scrape
SCRAPE_LANGUAGE = 'en' # Scraping language
SCRAPE_SOURCES = [] # Strings containing sources to scrape, empty list = any sources
VERBOSE = True # Verbose mode

class article_schema(SchemaClass):
    title = TEXT(stored=True)
    description = TEXT(stored=True)
    source = TEXT(stored=True)
    URL = TEXT(stored=True)
    date = DATETIME(stored=True)

json_file = None

# INITIALIZING INDEX
ix = None
if not os.path.exists(ARTICLE_INDEX_NAME):
    os.mkdir(ARTICLE_INDEX_NAME)
    ix = index.create_in(ARTICLE_INDEX_NAME, article_schema)
else:
    ix = index.open_dir(ARTICLE_INDEX_NAME)

# SCRAPING AND WRITING
SCRAPE_START_DATE = datetime.strptime(SCRAPE_START_DATE, '%m/%d/%Y')
start_date = SCRAPE_START_DATE

while start_date.date() < datetime.today().date():
    end_date = start_date + timedelta(days=(SCRAPE_PERIOD-1))
    scrape_dates = (start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y'))
    print("Scraping dates: " + str(scrape_dates))
    article_json = GetGoogleArticles(topic=SCRAPE_TOPIC, sources=SCRAPE_SOURCES, verbose=VERBOSE, time_range=scrape_dates, language=SCRAPE_LANGUAGE, pages=SCRAPE_PAGES)


    if article_json['status'] == 200:
        articles_saved = 0
        if VERBOSE:
            print("Got {0} articles in {1} seconds, recording in index".format(article_json['results'], article_json['time_taken']))
        writer = AsyncWriter(ix)
        for article in article_json['articles']:
            if article['title'] != "" and article['desc'] != "" and article['media'] != "" and article['datetime'] != "" and article['link'] != "":
                article_datetime = datetime.strptime(article['datetime'], '%m/%d/%Y')
                writer.add_document(title=article['title'], description=article['desc'], source=article['media'], URL=article['link'], date=article_datetime)
                articles_saved += 1
                if JSON_RECORD:
                    write_dict = {"title":article['title'], "description":article['desc'], "source":article['media'], "URL":article['link'], "date":article['datetime']}
                    json_file = open("ScrapeDatabase.json", "a")
                    json_file.write(json.dumps(write_dict) + ",\n")
                    json_file.close()
        writer.commit()
        print("Kept {} articles".format(articles_saved))
    else:
        print("Failed to get articles with code {0}\nError: {1}".format(article_json['code'], article_json['message']))
    
    print("Sleeping for {} seconds".format(SCRAPE_DELAY))
    sleep(SCRAPE_DELAY)

    start_date = start_date + timedelta(days=(SCRAPE_PERIOD))
    if VERBOSE:
        print("Beginning scraping for {}".format(start_date.strftime('%m/%d/%Y')))
