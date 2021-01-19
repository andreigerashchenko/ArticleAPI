import json
from time import time
from datetime import datetime, timedelta
from GoogleNews import GoogleNews

def GetGoogleArticles(topic = None, sources = [], language='en', time_range = None, time_period = None, encoding = 'utf-8', pages = 3, verbose = False):
    """Get a JSON object containing Google News article data



    Arguments:
        topic (string) - A keyword for searching articles
                Could in theory be multiple words (untested)
        sources (list) - A list of strings for specifying sources
                Can either be just source names or formatted as
                "site:example.com" for more accurate results
        lang (string) - The language to use for searching
                English by default
        time_range (tuple) - A tuple containing the start and end times
                Example: ('02/01/2020','02/28/2020')
        time_period (string) - How far back to search, starting from the current date in days
                Example: "7d" for one week. This will override the time_range argument
        encoding (string) - Encoding to use in the returned JSON
                UTF-8 by default
        pages (int) - How many pages to scrape
                3 by default, each page has roughly 10-20 articles
        verbose (bool) - Whether to show verbose output
                False by default

    Returns:
        A string formatted JSON object with a status code, result quantity,
        processing time , and a list of articles
        containing a title, URL, source name, and the article description"""

    start_time = time()
    return_json = {'status': 200, 'results': 0, 'time_taken': 0, 'articles': []}
    search_string = ""

    if verbose:
        print("Running in verbose mode...")

    if topic is None:
        return_json['time_taken'] = round((time() - start_time), 2)
        if verbose:
            print("Returning empty article list")
        return json.dumps(return_json)
    else:
        search_string = topic

    googlenews = GoogleNews(lang=language, encode=encoding)

    if len(sources) > 0:
        for source in sources:
            if verbose:
                print("Adding source {0}".format(str(source)))
            search_string += (" " + str(source))

    if time_period is not None:
        googlenews.set_period(time_period)
        if verbose:
            print("Using a time period of {}".format(time_period))
    elif time_range is not None:
        googlenews.set_time_range(time_range[0], time_range[1])
        # start_date = datetime.strptime(time_range[0], '%m/%d/%Y') - timedelta(days=1)
        # end_date = datetime.strptime(time_range[1], '%m/%d/%Y') + timedelta(days=1)
        # search_string += (" after:{} before:{}".format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        if verbose:
            # print("Using a time range of {0} to {1}".format(start_date.strftime('%m/%d/%Y'), end_date.strftime('%m/%d/%Y')))
            print("Using a time range of {0} to {1}".format(time_range[0], time_range[1]))
    else:
        googlenews.set_period('7d')
        if verbose:
            print("Using default time period of 7d")

    if verbose:
        print("Current search string: {0}".format(str(search_string)))

    googlenews.search(search_string)

    for i in range(1, pages + 1):
        if verbose:
            print("Getting page {}".format(i))
        if i > 1:
            googlenews.get_page(page=i)
        for result in googlenews.results():
            if isinstance(result['datetime'], datetime):
                result['datetime'] = result['datetime'].strftime('%m/%d/%Y')
            return_json['articles'].append(result)
            return_json['results'] += 1
            if verbose:
                print("\nResult: {}".format(str(result)))

    return_json['time_taken'] = round((time() - start_time), 2)

    return return_json

def __main():
    print("This is only for testing. If you weren't expecting to read this, you are probably doing something wrong")
    sourcelist = []
    newstopic = input("Enter a topic: ")
    newssource = input("Enter source(s): ")
    if newssource != "":
        sourcelist.append(newssource)

    scrape_range = ('1/1/2020', '6/1/2021')
    news_json = GetGoogleArticles(topic=newstopic, sources=sourcelist, verbose=True, time_range=scrape_range)
    with open(('CustomNewsAPI' + newstopic + '.json'), 'w') as output_file:
        json.dump(news_json, output_file, indent=2)
        print("Saved article results to {}.json".format(newstopic))

if __name__ == "__main__":
    __main()
