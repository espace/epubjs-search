from flask import Flask
from flask import request
from flask import jsonify
from flask import g

from epubsearch import EpubIndexer
from epubsearch import crossdomain
from optparse import OptionParser
import os

app = Flask(__name__)

@app.route("/search", methods=['GET','OPTIONS'])
@crossdomain(origin='*')

def search():
    """
    Search action method takes 3 paramaters:
    q: query (Mandtory)
    id: book_id to search into (Mandtory)
    exact_match: exact match flag (Mandtory, Default: False)
    """
    global container_path
    query       = request.args.get('q')
    book_id     = request.args.get('id')
    exact_match = request.args.get('exact_match')
    with_word_source = request.args.get('with_word_source')
    index_path  = os.path.join('databases', book_id)

    if(os.path.isdir(index_path) and len(query) >= 3):
        index   = EpubIndexer("whoosh", book_id)
        results = index.search(query, exact_match=exact_match, with_word_source=with_word_source)
        return jsonify(**results)

    return jsonify(results=[])

def flaskrun(app):
    """
    Takes a flask.Flask instance and runs it. Parses command-line flags to configure the app.
    """
    parser = OptionParser()
    parser.add_option('-d', '--debug',help="set to True to enable debug, Dont enable debug in production", dest='debug')
    (options, args) = parser.parse_args()

    if not options.debug:
        options.debug=False

    # Make sure debug is set to false in production
    app.run(debug=options.debug)

if __name__ == "__main__":
    flaskrun(app)
