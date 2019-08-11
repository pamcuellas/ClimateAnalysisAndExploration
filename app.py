#################################################
# Import dependencies
#################################################
import numpy as np
import datetime 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Validate date
#################################################
def check_valid_date(str_dt):
    valid = True
    try:
        datetime.datetime.strptime(str_dt, '%Y-%m-%d')
    except ValueError:
        valid = False
    return valid

#################################################
# Flask Routes
#################################################

############################## Root Route ##############################   
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

############################## Precipitation ##############################   
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns a list of date and precipitation"""

    # Query precipitation
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).limit(2000).all()
    lst_result = [] 
    for result in results:
        lst_result.append({ f'"{result.date}"':result.prcp})     
    return jsonify(lst_result)


############################## Stations ##############################   
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

############################## Tobs ############################## 
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

############################## Start Date ############################## 
@app.route("/api/v1.0/<dt_start>")
def start(dt_start):
    """Returns the minimum temperature, the average temperature, and the max temperature for a given start date"""

    # Validate dates:
    if not check_valid_date(dt_start):
        return jsonify({"error": f"The starting date is not valid. You might consider checking the format ({dt_start}), must be YYYY-MM-DD."}), 404

    # Query stats period
    session = Session(engine)
    sel = [ func.min(Measurement.tobs).label("TMIN"),\
            func.max(Measurement.tobs).label("TAVG"),\
            func.avg(Measurement.tobs).label("TMAX")
            ]
    results = session.query(*sel).filter(Measurement.date >= dt_start).all()
    if results[0].TMIN is not None:
        lst_result = [] 
        lst_result.append( {'"TMIN"':results[0].TMIN, '"TAVG"':results[0].TAVG, '"TMAX"':results[0].TMAX } )       
        return jsonify(lst_result)

    return jsonify({"error": f"No data found for the starting date {dt_start}."}), 404

############################## Start and End Dates ############################## 
@app.route("/api/v1.0/<dt_start>/<dt_end>")
def period(dt_start, dt_end):
    """Returns the minimum temperature, the average temperature, and the max temperature for a given start or start-end range"""

    # Validate dates:
    if not check_valid_date(dt_start) or not check_valid_date(dt_end):
        return jsonify({"error": f"At least one date is not valid. You might consider checking the format ({dt_start} - {dt_end}), must be YYYY-MM-DD."}), 404

    # Query stats period
    session = Session(engine)
    sel = [ func.min(Measurement.tobs).label("TMIN"),\
            func.max(Measurement.tobs).label("TAVG"),\
            func.avg(Measurement.tobs).label("TMAX")
            ]
    results = session.query(*sel).filter(Measurement.date >= dt_start, Measurement.date <= dt_end).all()
    if results[0].TMIN is not None:
        lst_result = [] 
        lst_result.append( {'"TMIN"':results[0].TMIN, '"TAVG"':results[0].TAVG, '"TMAX"':results[0].TMAX } )       
        return jsonify(lst_result)

    return jsonify({"error": f"No data found for period between {dt_start} and {dt_end}."}), 404


if __name__ == '__main__':
    app.run(debug=True)