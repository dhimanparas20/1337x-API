from flask import Flask, request
from flask_restful import Resource, Api
import logging
from sites.one337x.api import fetch as fetch_1337x
from sites.pirate_bay.api import fetch as fetch_pb

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a Flask application
app = Flask(__name__)
api = Api(app)

class Search1337x(Resource):
    def get(self, query=None, category=None, pgno=None):
        userAgent = request.headers.get('User-Agent')
        
        if not query:
            query = request.args.get('q')
            
        if not category:
            category = request.args.get('category')

        if pgno is None:
            # Fallback to query param or default
            pgno = request.args.get('page')

        # fetch_1337x signature: (query, category, pgno, userAgent)
        data = fetch_1337x(query, category, pgno, userAgent)
        return data

class SearchPirateBay(Resource):
    def get(self, query=None, category=None, pgno=None):
        userAgent = request.headers.get('User-Agent')
        
        if not query:
            query = request.args.get('q')
            
        if not category:
            category = request.args.get('category')

        if pgno is None:
            # Fallback to query param or default
            pgno = request.args.get('page')

        # fetch_pb signature: (query, category, pgno, userAgent)
        data = fetch_pb(query, category, pgno, userAgent)
        return data

# Add resources to the API
# Order matters for routing: specific first
api.add_resource(Search1337x, 
                 '/1337x/<query>/<category>/<int:pgno>', 
                 '/1337x/<query>/<int:pgno>', 
                 '/1337x/<query>/<category>', 
                 '/1337x/<query>', 
                 '/1337x/')

api.add_resource(SearchPirateBay, 
                 '/pirate-bay/<query>/<category>/<int:pgno>', 
                 '/pirate-bay/<query>/<int:pgno>', 
                 '/pirate-bay/<query>/<category>', 
                 '/pirate-bay/<query>', 
                 '/pirate-bay/')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0", threaded=True)
