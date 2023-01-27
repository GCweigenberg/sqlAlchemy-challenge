import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from flask import Flask, jsonify
import datetime as dt

# set up a database

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
base = automap_base()
base.prepare(engine, reflect=True)

Measurement = base.classes.measurement
Station = base.classes.station


# flask
app = Flask(__name__)


@app.route('/')
def welcome():
    """List all available api routes"""
    return (
        f"Hey, Hi, Hello Here are the Avaiable Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Station List: /api/v1.0/stations<br/>"
        f"One Year Temperature at a Glance: /api/v1.0/tobs<br/>"
        f"Start date Temperature(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Start to End date Temperature(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # session link
    session = Session(engine)

    """list of all precipitation"""

    day_one = '2016-08-24'

    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date <= day_one).all()

    session.close()

    # convert to dictionary
    all_precipitation = []

    for prcp, date in precipitation:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp

        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """List of active stations"""
    sel = [Measurement.station]
    active_stations = session.query(*sel).group_by(Measurement.station).all()
    session.close()

    station_list = list(np.ravel(active_stations))
    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    day_one = '2016-08-23'
    sel = [Measurement.date, Measurement.tobs]

    temperatures = session.query(*sel).filter(Measurement.date >= day_one, Measurement.station == 'USC00519281').group_by(Measurement.date).order_by(Measurement.date).all()

    session.close()

    # convert to dictionary
    dates_observed = []
    observed_temperatures = []

    for date, observation in temperatures:
        dates_observed.append(date)
        observed_temperatures.append(observation)

    active_tobs_dictionary = dict(zip(dates_observed, observed_temperatures))

    return jsonify(active_tobs_dictionary)


@app.route("/api/v1.0//<day_one>")
def first_day(day_one, last_day='2017-08-23'):

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= day_one).filter(Measurement.date <= last_day).all()
    session.close()

    start_day_record = []
    for min, avg, max in results:
        start_day_dict = {}
        start_day_dict["Min_temp"] = min
        start_day_dict["Avg_temp"] = avg
        start_day_dict["Max_temp"] = max
        start_day_record.append(start_day_dict)
    return jsonify(start_day_record)


@app.route('/api/v1.0/<day_one>/<last_day>')
def last_day(day_one, last_day='2017-08-23'):

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= day_one).filter(Measurement.date <= last_day).all()
    session.close()
    print(results)
    last_day_record = []
    for min, avg, max in results:
        last_day_dict = {}
        last_day_dict["Min_temp"] = min
        last_day_dict["Avg_temp"] = avg
        last_day_dict["Max_temp"] = max
        last_day_record.append(last_day_dict)
    return jsonify(last_day_record)

 
if __name__ == "__main__":
    app.run(debug=True)
