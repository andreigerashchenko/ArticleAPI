import json
import sys
import requests
from time import time
from newspaper import Article

NEWS_API_URL = "https://api.andreigerashchenko.com/newsapi"
VERBOSE = False

def get_processed_articles(topic = None, source = None, start_date = None, end_date = None, amount = 50, combine = True, verbose = False):
    """Get a JSON file containing article data

    

    Arguments:
        topic (string) - A keyword for searching articles
                Could in theory be multiple words (untested)
        verbose (bool) - Whether to show verbose output

    Returns: 
        A JSON file with a status code, result quantity,
        processing time (including article parsing), and a list of articles
        containing a title, URL, source name, and the article text"""

    start_time = time()
    if verbose:
        print("Running in verbose mode")
    added_first_argument = False
    api_request = NEWS_API_URL
    return_data = {'status': 200, 'results': 0, 'time_taken': 0, 'articles': []}

    if topic is not None:
        if not added_first_argument:
            api_request += "?topic={}".format(topic)
            added_first_argument = True
        else:
            api_request += "&topic={}".format(topic)
    if source is not None:
        if not added_first_argument:
            api_request += "?source={}".format(source)
            added_first_argument = True
        else:
            api_request += "&source={}".format(source)
    if start_date is not None and end_date is not None:
        if not added_first_argument:
            api_request += "?start_date={0}&end_date={1}".format(start_date, end_date)
            added_first_argument = True
        else:
            api_request += "&start_date={0}&end_date={1}".format(start_date, end_date)
    if amount is not None:
        if not added_first_argument:
            api_request += "?amount={}".format(amount)
            added_first_argument = True
        else:
            api_request += "&amount={}".format(amount)
    if combine is not None:
        if not added_first_argument:
            api_request += "?combine={}".format(combine)
            added_first_argument = True
        else:
            api_request += "&combine={}".format(combine)
    
    if verbose:
        print("API request URL: {}".format(api_request))
    news_api_json = requests.get(api_request).json()

    if verbose:
        print("Response status: {}".format(news_api_json['status']))

    if news_api_json['status'] == 200:
        for article in news_api_json['articles']:
            parsed_article = Article(article['URL'])
            try:
                parsed_article.download()
            except Exception as e:
                if (VERBOSE or verbose):
                    print("Failed to download article {} with exception {}, skipping".format(article['URL'], e))
                continue
            try:
                parsed_article.parse()
            except Exception as e:
                if (VERBOSE or verbose):
                    print("Failed to parse article {} with exception {}, skipping".format(article['URL'], e))
                continue

            title = article['title']
            url = article['URL']
            sourcename = article['source']

            if (VERBOSE or verbose):
                print("Parsed article " + url)

            article_object = {'title': title, 'url': url, 'sourcename': sourcename, 'articletext': parsed_article.text}
            return_data['articles'].append(article_object)
            return_data['results'] = return_data['results'] + 1
        return_data['time_taken'] = round((time() - start_time), 2)

    elif (news_api_json['code'] in ['apiKeyDisabled', 'apiKeyExhausted', 'apiKeyInvalid', 'apiKeyMissing', 'rateLimited']):
        # Handle API key errors
        return_data = {'status': 401, 'code': news_api_json['code'], 'message': news_api_json['message']}
    elif (news_api_json['code'] in ['badArguments', 'parameterInvalid', 'parametersMissing', 'sourcesTooMany', 'sourceDoesNotExist']):
        # Handle request errors
        return_data = {'status': 400, 'code': news_api_json['code'], 'message': news_api_json['message']}
    else: # Handle anything else (likely not our fault)
        return_data = {'status': 500, 'code': news_api_json['code'], 'message': news_api_json['message']}

    return return_data

def __main(argv):
    if len(argv) == 1:
        print("Usage: news.py [topic] [Verbose (default false)]")
        exit()

    news_json = get_processed_articles(topic=argv[1], verbose=VERBOSE)

    if news_json['status'] == 200:
        for article in news_json['articles']:
            print("=======================================================================")
            print("Article title: " + article['title'])
            print("Article URL: " + article['URL'])
            print("Article source name: " + article['sourcename'])
            print("Full article text: " + article['articletext'])
        print("=======================================================================")
        print("Got {} articles in {} seconds".format(news_json['results'], news_json['time_taken']))
    else:
        print("An error has occurred:")
        print("Status code " + news_json['status'])
        print("Error code " + news_json['code'])
        print("Error description " + news_json['message'])

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        if (sys.argv[2] == 'True' or sys.argv[2] == 'true'):
            VERBOSE = True
        else:
            VERBOSE = False
    else:
        VERBOSE = False

    __main(sys.argv)
else:
    USE_LOCAL_DATA = False
    VERBOSE = False
