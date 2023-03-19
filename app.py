from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return (f"available routes: <br/>"
    f"/api/v1.0/precipitation <br/>"
    f"/api/v1.0/stations <br/>"
    f"/api/v1.0/tobs <br/>"
    f"/api/v1.0/YYYY-MM-DD <br/>"
    f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD <br/>"
    f"<form action='/api/v1.0/tempature' method='get'>\
            <label>Start Date:</label><br>\
            <input type='text' name='startdate' value='' placeholder='YYY-MM-DD'><br>\
            <label>End Date:</label><br>\
            <input type='text' name='enddate' value='' placeholder='YYY-MM-DD'><br>\
            <input type='submit' value='Submit'>\
        </form>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    session.close()
    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    
    station_list = list(np.ravel(results))
    return jsonify(stations=station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()
    
    temps = list(np.ravel(results))
    return jsonify(temperature=temps)


@app.route("/api/v1.0/<startdate>")
@app.route("/api/v1.0/<startdate>/<enddate>")
def stats(startdate=None, enddate=None):
    sql = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]
    
    if not enddate:
        
        results = session.query(*sql).\
            filter(Measurement.date >= startdate).all()
    else:
        
        results = session.query(*sql).\
            filter(Measurement.date >= startdate).\
            filter(Measurement.date <= enddate).all()
    
    temps = list(np.ravel(results))
   
    return jsonify(temperatures=temps)


@app.route("/api/v1.0/tempature", methods=['GET'])
def tempature():
    
    # startdate = request.form["startdate"]
    # startdate = request.form.get("startdate", "")
    # enddate = request.form["enddate"]
    
    # startdate = request.args.get("startdate", "")
    # enddate = request.args.get("enddate", "")
    
    startdate = request.args["startdate"]
    enddate = request.args["enddate"]
    
    print("\n=================================================")
    print(f"startdate: {startdate}    enddate: {enddate}")
    print("=================================================\n")

    sql = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]
    
    if not enddate:
        # Calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sql).\
            filter(Measurement.date >= startdate).all()
    else:
        # Calculate TMIN, TAVG, TMAX with start and stop
        results = session.query(*sql).\
            filter(Measurement.date >= startdate).\
            filter(Measurement.date <= enddate).all()
    
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    # Results
    return jsonify(temps=temps)



if __name__ == "__main__":
    app.run(debug=True)


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=7000, debug=True)
