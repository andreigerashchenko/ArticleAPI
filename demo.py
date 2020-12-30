import json
from news import get_processed_articles

topic = input("Enter a topic: ")

article_response = get_processed_articles(topic, True)

news_json = json.loads(article_response)

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

with open((topic + '.json'), 'w') as output_file:
    json.dump(news_json, output_file, indent=2)
    print("Saved article results to {}.json".format(topic))
