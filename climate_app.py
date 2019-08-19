import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurements = Base.classes.measurement
Stations = Base.classes.station

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
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of measurement data including the date and prcp"""
    # Query all observation dates
    results = session.query(Measurements.date, Measurements.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation by dates
    prcp_by_date = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        prcp_by_date.append(prcp_dict)

    return jsonify(prcp_by_date)

@app.route("/api/v1.0/station")
def stat():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Stations.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tob():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temperatures"""
    # Query all dates
    results = session.query(Measurements.date, Measurements.tobs).\
            filter(Measurements.date >= dt.datetime.strptime(session.query(func.max(Measurements.date)).all()[0][0], "%Y-%m-%d")-dt.timedelta(days = 366)).all()

    session.close()

    tobs_lastyear = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_lastyear.append(tobs_dict)

    return jsonify(tobs_lastyear)

@app.route("/api/v1.0/<start>")
def start_tob(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temperatures starting at date entered"""
    # Query all dates
    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs),func.max(Measurements.tobs)).\
            filter(Measurements.date >= dt.datetime.strptime(start, "%Y-%m-%d")).all()

    session.close()

    keys = ["TMin","TAvg","TMax"]
    
    start_tobs_out = []
    for i in range(3):
        start_tobs_dict = {keys[i]:results[0][i]}
        start_tobs_out.append(start_tobs_dict)

    return jsonify(start_tobs_out)

@app.route("/api/v1.0/<start>/<end>")
def se_tob(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all temperatures between the dates entered"""
    # Query all dates
    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs),func.max(Measurements.tobs)).\
            filter(Measurements.date >= dt.datetime.strptime(start, "%Y-%m-%d")).\
                filter(Measurements.date <= dt.datetime.strptime(end, "%Y-%m-%d")).all()

    session.close()
    
    keys = ["TMin","TAvg","TMax"]
    
    se_tobs_out = []
    for i in range(3):
        se_tobs_dict = {keys[i]:results[0][i]}
        se_tobs_out.append(se_tobs_dict)

    return jsonify(se_tobs_out)

if __name__ == '__main__':
    app.run(debug=True)

