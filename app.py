from flask import Response, Flask, request, abort, render_template
from flask import jsonify
from datetime import datetime
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps

#Create a engine for connecting to SQLite3.
#Assuming geo_example.db is in your app root folder

e = create_engine('sqlite:///geo_example.db')

app = Flask(__name__)
api = Api(app)

# def dict_factory(cursor, row):
#     d = {}
#     for idx,col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response


@app.route("/")
def Home():
    return render_template("index.html")
    #Was having an html template rendering error because of the Class object and get method:
    #the response was being generated in mime type json instead of html.


class Name_of_Places(Resource):
    def get(self):
        #Connect to databse
        conn = e.connect()
        #Perform query and return JSON data
        query = conn.execute("select Name from geo_example")
        MyList = list (i[0] for i in query.cursor.fetchall())
        return jsonify ({'places':MyList})
        #Selects only the first position of the cursor (names), among all the rows

class Init_Hour_Info(Resource):
    def get(self, hour_of_visit):
        if not (0 <= hour_of_visit <= 2359):
            abort (400) # Bad request
        conn = e.connect()
        query = conn.execute("select * from geo_example where init_hour='%d'"%hour_of_visit)
        MyList = list (dict(zip (tuple (query.keys()) ,i)) for i in query.cursor)
        #Query the result and get cursor.Dumping that data to a JSON is looked by extension
        #result = {'inital_hour': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        #Creates a dictionary containing a zipped tuple of the query keys (column names) and their corresponding values
        return jsonify ({'inital_hour':MyList})

class Visits_on_Date(Resource):
    def get(self, date_of_visit):
        if (date_of_visit < '2015-01-01'):
            abort (400) #Bad request: this example supports only data from 2015 and 2016
        conn = e.connect()
        query = conn.execute("select * from geo_example where date='%s'"%date_of_visit)
        MyList = list ([i[0] for i in query.cursor.fetchall()])
        #result = {'visits on %s'%date_of_visit: [i[0] for i in query.cursor.fetchall()]}
        return jsonify ({'visits on %s'%date_of_visit: MyList})

class Visits_Betweeen_Dates(Resource):
    def get(self, left_limit_date, right_limit_date):
        if (left_limit_date >= right_limit_date):
            abort (400) #Bad request: left limit defines the oldest date
        conn = e.connect()
        query = conn.execute("select * from geo_example where date between '%s' and '%s'"%(left_limit_date, right_limit_date))
        MyList = list ([i[0] for i in query.cursor.fetchall()])
        #result = {'visits between %s and %s'%(left_limit_date, right_limit_date): [i[0] for i in query.cursor.fetchall()]}
        return jsonify ({'visits between %s and %s'%(left_limit_date, right_limit_date): MyList})

class List_of_Init_Hours(Resource):
    def get(self):
        conn = e.connect()
        query = conn.execute("select init_hour from geo_example")
        MyList = list (i[0] for i in query.cursor.fetchall())
        return jsonify ({'initial_hours':MyList})


api.add_resource(Init_Hour_Info, '/visits/<int:hour_of_visit>')
api.add_resource(Name_of_Places, '/places')
api.add_resource(Visits_on_Date, '/visits/onDate/<date_of_visit>')
api.add_resource(Visits_Betweeen_Dates, '/visits/between/<left_limit_date>/<right_limit_date>')
api.add_resource(List_of_Init_Hours, '/hours')
#api.add_resource(Home, '/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
