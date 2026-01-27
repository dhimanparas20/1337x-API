from flask import Flask, request
from flask_restful import Resource, Api
from sites.one337x.api import fetch as fetch_1337x
from sites.pirate_bay.api import fetch as fetch_pb

# Create a Flask application
app = Flask(__name__)
api = Api(app)

class Search1337x(Resource):
    def get(self, pgno=1, query=None):
        userAgent = request.headers.get('User-Agent')
        if not query:
            query = request.args.get('q')
            pgno = request.args.get('page')
        data = fetch_1337x(query, pgno, userAgent)
        return data

class SearchPirateBay(Resource):
    def get(self, pgno=0, query=None):
        userAgent = request.headers.get('User-Agent')
        if not query:
            query = request.args.get('q')
            pgno = request.args.get('page')
        data = fetch_pb(query, pgno, userAgent)
        return data

# Add resources to the API
api.add_resource(Search1337x, '/1337x/', '/1337x/<query>', '/1337x/<query>/<int:pgno>')
api.add_resource(SearchPirateBay, '/pirate-bay/', '/pirate-bay/<query>', '/pirate-bay/<query>/<int:pgno>')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0", threaded=True)
