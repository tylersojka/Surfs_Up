#import general dependencies
import datetime as dt
import numpy as np
import pandas as pd
#import all the sqlalchemy dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#import the flask dependencies
from flask import Flask, jsonify



# set up the database engine to access the sqlite database
engine = create_engine("sqlite:///hawaii.sqlite")

# function to allow us to access and query our sqlite database file
Base = automap_base()

# reflect the database
Base.prepare(engine, reflect=True)

# assign variables to the two table references
Measurement = Base.classes.measurement
Station = Base.classes.station

#create a session link from python to our database
session = Session(engine)


################################
# set up flask
#################################

#create a new flask app instance
app = Flask(__name__)

# create the first route
@app.route('/')
def welcome():
    return(
    f'Welcome to the Climate Analysis API!<br>'
    f'Available Routes:<br>'
    f'<a href="/api/v1.0/precipitation"> /api/v1.0/precipitation: Last Year of Percipitation </a><br>'
    f'<a href="/api/v1.0/stations"> /api/v1.0/stations: All Opperating Recording Stations </a><br>'
    f'<a href="/api/v1.0/tobs"> /api/v1.0/tobs: All temperature observations from the most active station in the last year </a><br>'
    f'/api/v1.0/temp/start: All temperature observations from yyyy/mm/dd - most recent entry <br>'
    f'/api/v1.0/temp/start/end All observed temperatures between given date yyyy,mm,dd/yyyy/mm/dd<br>'
    )

#create second route (precipitation)
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

# create 3rd route, stations
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()  # get all the stations in our db
    stations = list(np.ravel(results))  # convert unraveled  results into a list
    return jsonify(stations=stations)
   


# create 4th route, tobs
@app.route("/api/v1.0/tobs")
def tobs():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()
    # temps = list(np.ravel(results))
    # return jsonify(temps=temps)
    #return jsonify(list(np.ravel(results)))

    temps = {date: temp for date, temp in results}
    return jsonify(temps)


# create the 5th route, stats
@app.route('/api/v1.0/temp/<start>')
def start(start):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/temp/<start>/<end>')
def startEnd(start, end):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= start)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= end)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)