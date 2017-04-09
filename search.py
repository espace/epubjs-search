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
    global container_path
    query       = request.args.get('q')
    book_id     = request.args.get('id')
    exact_match = request.args.get('exact_match')
    path_prefix = container_path
    index_path  = os.path.join(path_prefix, book_id, 'search_index')

    if(os.path.isdir(index_path) and len(query) >= 3):
        index   = EpubIndexer("whoosh", index_path)
        results = index.search(query, exact_match=exact_match)
        return jsonify(**results)

    return jsonify(results=[])

def flaskrun(app):
    """
    Takes a flask.Flask instance and runs it. Parses command-line flags to configure the app.
    """
    parser = OptionParser()
    parser.add_option('-p', '--path',help='Path to the container folder that contains epub unzipped folders', dest='container_path')
    parser.add_option('-d', '--debug',help="set to True to enable debug, Dont enable debug in production", dest='debug')
    (options, args) = parser.parse_args()

    if not options.container_path:
        options.container_path = os.getcwd()

    if not options.debug:
        options.debug=False

    # set path in global varaiable so i can access it in the search method
    global container_path
    container_path = options.container_path
    # Make sure debug is set to false in production
    app.run(debug=options.debug)

if __name__ == "__main__":
    flaskrun(app)
