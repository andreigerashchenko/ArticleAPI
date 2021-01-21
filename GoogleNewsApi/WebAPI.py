import flask
import config
from datetime import datetime
from flask import request, jsonify
from time import time
from whoosh import index
from whoosh.query import DateRange
from whoosh.qparser import QueryParser
from whoosh.searching import Results

app = flask.Flask(__name__)
app.config["DEBUG"] = True

valid_request_json = {'status': 200, 'results': 0, 'time_taken': 0, 'articles': []}
bad_arg_json = {'status': 400, 'code': 'badArguments', 'message': 'No arguments provided'}

@app.route('/', methods=['GET'])
def home():
    return '''<h1>If I haven't told you about this, this isn't for you</h1>'''


@app.route('/newsapi', methods=['GET'])
def api_id():
    start_time = time()
    arguments_used = 0
    amount_needed = 50
    results_list = []
    combine_results = False

    
    # Handle individual arguments
    if 'amount' in request.args:
        amount_needed = int(request.args['amount'])
    if 'combine' in request.args:
        if bool(request.args['combine']) == True:
            combine_results = True

    if 'source' in request.args:
        arguments_used += 1
        source_arg = str(request.args['source'])

        ix = index.open_dir(config.ARTICLE_INDEX_NAME, readonly=True)

        query_parser = QueryParser("source", schema=ix.schema)
        query = query_parser.parse(source_arg)
        searcher = ix.searcher()
        results = searcher.search(query, limit=amount_needed)
        results_list.append(results)

    if 'start_date' in request.args and "end_date" in request.args:
        arguments_used += 1
        start_date = datetime.strptime(str(request.args['start_date']), "%m-%d-%Y")
        end_date = datetime.strptime(str(request.args['end_date']), "%m-%d-%Y")


        ix = index.open_dir(config.ARTICLE_INDEX_NAME, readonly=True)

        query = DateRange("date", start_date, end_date)
        searcher = ix.searcher()
        results = searcher.search(query, limit=amount_needed)
        results_list.append(results)
    if 'topic' in request.args:
        arguments_used += 1
        topic = str(request.args['topic'])

        ix = index.open_dir(config.ARTICLE_INDEX_NAME, readonly=True)
        searcher = ix.searcher()

        title_query_parser = QueryParser("title", schema=ix.schema)
        title_query = title_query_parser.parse(topic)
        desc_query_parser = QueryParser("description", schema=ix.schema)
        desc_query = desc_query_parser.parse(topic)
        
        title_results = searcher.search(title_query, limit=amount_needed)
        desc_results = searcher.search(desc_query, limit=amount_needed)
        title_results.upgrade_and_extend(desc_results)
        results_list.append(title_results)

        print("TYPE: {}".format(type(title_results)))

    # Handle bad/empty requests
    if arguments_used == 0:
        response = jsonify(bad_arg_json)
        # searcher.close()
        return response


    # Loop through results and combine if necessary
    return_json = valid_request_json
    return_json['results'] = 0
    return_json['articles'] = []
    if (len(results_list) > 0):
        main_result = results_list[0]
        if len(results_list) > 1:
            for result in results_list:
                if main_result != result:
                    main_result.upgrade(result)
        
        articles_saved = 0
        print("Before adding results: {}".format(len(return_json['articles'])))
        for article in main_result:
            if articles_saved < amount_needed:
                current_article = article.fields()
                current_article.pop('ID', None)
                return_json['articles'].append(current_article)
                
                articles_saved += 1
                # print("Added article {}".format(article.fields()['title']))
            else:
                # print("Reached article limit ({0} out of {1})".format(articles_saved, amount_needed))
                pass

    return_json['time_taken'] = round((time() - start_time), 2)
    return_json['results'] = len(return_json['articles'])
    print("Results: {}".format(len(return_json['articles'])))
    response = jsonify(return_json)
    
    return_json = valid_request_json
    print("Cleared Results: {}".format(len(return_json['articles'])))
    print("Request json Results: {}".format(len(valid_request_json['articles'])))
    searcher.close()
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port='8246')
