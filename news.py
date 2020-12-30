import json
import sys
from time import time
from newsapi import NewsApiClient
from newspaper import Article
import API_Keys

newsApiInstance = NewsApiClient(api_key=API_Keys.NEWSAPI_KEY)

def get_processed_articles(topic, verbose = False):
    """Get a JSON object containing article data

    

    Arguments:
        topic (string) - A keyword for searching articles
                Could in theory be multiple words (untested)
        verbose (bool) - Whether to show verbose output

    Returns: 
        A string formatted JSON object with a status code, result quantity,
        processing time (including article parsing), and a list of articles
        containing a title, URL, source name, and the article text"""

    start_time = time()
    return_data = {'status': 200, 'results': 0, 'time_taken': 0, 'articles': []}

    if USE_LOCAL_DATA:
        if (VERBOSE or verbose):
            print("Using cached NewsAPI request data")
        news_api_json = TempJSONData
    else:
        if (VERBOSE or verbose):
            print("Using 1 NewsAPI API request")
        news_api_json = newsApiInstance.get_everything(q=topic)

    if news_api_json['status'] == 'ok':
        for article in news_api_json['articles']:
            parsed_article = Article(article['url'])
            try:
                parsed_article.download()
            except Exception as e:
                if (VERBOSE or verbose):
                    print("Failed to download article {} with exception {}, skipping".format(article['url'], e))
                continue
            try:
                parsed_article.parse()
            except Exception as e:
                if (VERBOSE or verbose):
                    print("Failed to parse article {} with exception {}, skipping".format(article['url'], e))
                continue

            title = article['title']
            url = article['url']
            sourcename = article['source']['name']

            if (VERBOSE or verbose):
                print("Parsed article " + url)

            article_object = {'title': title, 'url': url, 'sourcename': sourcename, 'articletext': parsed_article.text}
            return_data['articles'].append(article_object)
            return_data['results'] = return_data['results'] + 1
        return_data['time_taken'] = round((time() - start_time), 2)

    elif (news_api_json['code'] in ['apiKeyDisabled', 'apiKeyExhausted', 'apiKeyInvalid', 'apiKeyMissing', 'rateLimited']):
        # Handle API key errors
        return_data = {'status': 401, 'code': news_api_json['code'], 'message': news_api_json['message']}
    elif (news_api_json['code'] in ['parameterInvalid', 'parametersMissing', 'sourcesTooMany', 'sourceDoesNotExist']):
        # Handle request errors
        return_data = {'status': 400, 'code': news_api_json['code'], 'message': news_api_json['message']}
    else: # Handle anything else (likely not our fault)
        return_data = {'status': 500, 'code': news_api_json['code'], 'message': news_api_json['message']}

    return json.dumps(return_data)

def __main(argv):
    if len(argv) == 1:
        print("Usage: news.py [topic] [Use cached NewsAPI request (default true)] [Verbose (default false)]")
        exit()

    news_json = json.loads(get_processed_articles(argv[1]))

    if news_json['status'] == 200:
        for article in news_json['articles']:
            print("=======================================================================")
            print("Article title: " + article['title'])
            print("Article URL: " + article['url'])
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
        if (sys.argv[2] == 'False' or sys.argv[2] == 'false'):
            USE_LOCAL_DATA = False
        else:
            USE_LOCAL_DATA = True
    else:
        USE_LOCAL_DATA = True

    if len(sys.argv) >= 4:
        if (sys.argv[3] == 'True' or sys.argv[3] == 'true'):
            print("Running in verbose mode")
            VERBOSE = True
        else:
            VERBOSE = False
    else:
        VERBOSE = False

    if USE_LOCAL_DATA:
        #Use a saved copy of NewsAPI data for "q=bitcoin" to not waste API calls
        TempJSONFile = open('CachedNewsAPIRequest.json', encoding='utf-8')
        TempJSONData = json.load(TempJSONFile)

    __main(sys.argv)
else:
    USE_LOCAL_DATA = False
    VERBOSE = False
