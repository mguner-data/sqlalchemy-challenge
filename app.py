import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
Measurement=Base.classes.measurement
Station=Base.classes.station

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
        f"/api/v1.0/2017-01-01<br/>"
        f"/api/v1.0/2017-01-01/2017-02-03<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation"""
   
    # Perform a query to retrieve the data and precipitation scores
    query_date=dt.date(2017,8,23)-dt.timedelta(days=365)
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date>=query_date).all()

    session.close()
   # Create a new dictionary of date as the key and precipitation as the value
    prcp_dict = {}
    for one_list in prcp_results:
        prcp_dict[one_list[0]] = one_list[1]
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""

    # Perform a query

    stations_results = session.query(Station.station, Station.name).all()

    session.close()

   # Create a new dictionary
    station_dict = {}
    for one_list in stations_results:
        station_dict[one_list[0]] = one_list[1]
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperatures at location USC00519281"""
   
    # Perform a query to retrieve the data and precipitation scores
    query_date=dt.date(2017,8,23)-dt.timedelta(days=365)
    obs=session.query(Measurement.station, func.count(Measurement.tobs)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.tobs).desc()).all()
    top_station=obs[0][0]

    tops_results = session.query(Measurement.tobs).\
                filter(Measurement.date>=query_date).\
                filter(Measurement.station==top_station).all()

    session.close()

    all_tmp = list(np.ravel(tops_results))
    return jsonify(all_tmp)

@app.route("/api/v1.0/<start>")
def startdate(start):
    session=Session(engine)

    start_date1 = pd.to_datetime(start, format='%Y-%m-%d').date()
    #end_date = pd.to_datetime(endt, format='%Y-%m-%d').date()

    tmp_stats1= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date1).all()

    session.close()

    return jsonify(tmp_stats1)

@app.route("/api/v1.0/<startt>/<endt>")
def calc_temps(startt, endt):
    session=Session(engine)

    start_date = pd.to_datetime(startt, format='%Y-%m-%d').date()
    end_date = pd.to_datetime(endt, format='%Y-%m-%d').date()

    tmp_stats= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    return jsonify(tmp_stats)

if __name__ == '__main__':
    app.run(debug=True)
