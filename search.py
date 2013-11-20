from flask import Flask
from flask import request
from flask import jsonify

from epubsearch import EpubIndexer

app = Flask(__name__)
index = EpubIndexer("whoosh")

@app.route("/")
def home():
    return "try /search?q=whale"

@app.route("/search")
def search():
    query = request.args.get('q')
    results = index.search(query)
    return jsonify(**results)

if __name__ == "__main__":
    app.run(debug=True)
