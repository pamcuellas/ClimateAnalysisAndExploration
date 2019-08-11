import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns a list of date and precipitation"""

    # Query precipitation
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).limit(100).all()
    lst_result = [] 
    for result in results:
        lst_result.append({ f'"{result.date}"':result.prcp})     
    return jsonify(lst_result)


@app.route("/api/v1.0/stations")
def stations():
    """Returns the id, station, and name of all station"""
    # Query Stations
    session = Session(engine)
    results = session.query(Station.id, Station.station, Station.name).all()

    # Create a dictionary from the row data and append to a list of lst_stations
    lst_stations = []
    for id, station, name in results:
        dic_station = {'"id"':id, '"station"':station, '"name"':name }
        lst_stations.append(dic_station)
    return jsonify(lst_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of date and tobs of last year"""
    # Last data point was in 2017-08-23
    one_year_ago = "2016-08-24"
    # Query tobs
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs). \
        filter(Measurement.date >= one_year_ago).order_by(Measurement.date).all()
    lst_result = [] 
    for result in results:
        lst_result.append({ f'"{result.date}"':result.tobs})     
    return jsonify(lst_result)

    
if __name__ == '__main__':
    app.run(debug=True)