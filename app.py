from flask import Flask,redirect,request
from flask_restful import Resource, Api
from api import fetch

# Create a Flask application
app = Flask(__name__)
api = Api(app)
    
class Search(Resource):
    def get(self,pgno=1,query=None):
        userAgent = request.headers.get('User-Agent')
        if query:
            pass
        else:    
            query = request.args.get('q')
            pgno = request.args.get('page')          
        data = fetch(query,pgno,userAgent)       
        return data
          

# Add the HelloWorld resource to the API
api.add_resource(Search, '/','/<query>','/<query>/<int:pgno>')

if __name__ == '__main__':
    app.run(debug=True,port=5000,host="0.0.0.0",threaded=True)
