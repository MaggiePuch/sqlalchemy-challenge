# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Starter_Code\Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to Puch's Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (format: YYYY-MM-DD)<br/>" 
        f"/api/v1.0/start/end (format: YYYY-MM-DD/YYYY-MM-DD)<br/>" 
        f"Please note: Dates should fall between 2010-01-01 through 2017-08-23"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    recent_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()
    recent_date_str = recent_date_row[0]  

    # Calculate the date one year from the last date in data set.
    recent_date = dt.datetime.strptime(recent_date_str, '%Y-%m-%d').date()
    year_ago = recent_date - dt.timedelta(days=365)
    """Return a list of precipitation from last 12 months"""

    # Query all passengers
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date < recent_date).filter(measurement.date > year_ago).all()
    # Close Session
    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation 
    all_precipitation = []
    for date, prcp in results: 
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of all stations names"""
    # Query all stations
    station_names = session.query(station.station).all()
    # Close Session
    session.close()
    # Convert list of tuples into normal list
    all_station_names = list(np.ravel(station_names))

    return jsonify(all_station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Return a list of the most active station tobs""" 
    # Determine start date and end date using the tables:  
    recent_date_row = session.query(measurement.date).order_by(measurement.date.desc()).first()
    recent_date_str = recent_date_row[0]  
    # Calculate the date one year from the last date in data set.
    recent_date = dt.datetime.strptime(recent_date_str, '%Y-%m-%d').date()
    year_ago = recent_date - dt.timedelta(days=365)
    
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and return a list
    most_active_tobs = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date < recent_date).filter(measurement.date > year_ago).all()

    # Close Session
    session.close()

    # Convert list of tuples into normal list
    most_tobs = list(np.ravel(most_active_tobs))

    return jsonify(most_tobs)

@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a specified start date."""

    # Create query for tmin, tavg, and tmax tobs where date is greater than or equal to the date the user supplies in URL
    select_date = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    details = session.query(*select_date).filter(measurement.date >= start).all()
    # Close Session
    session.close()

    select_date_values = []
    for min, avg, max in details: 
        select_date_dict = {}
        select_date_dict['min'] = min
        select_date_dict['avg'] = avg
        select_date_dict['max'] = max
        select_date_values.append(select_date_dict)

    return jsonify(select_date_values)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a specified date range."""

    # Create query for tmin, tavg, and tmax tobs where date is greater than or equal to the date range the user supplies in URL
    select_date = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    details = session.query(*select_date).filter(measurement.date >= start).filter(measurement.date <= end).all()
    # Close Session
    session.close()

    select_date_values_range = []
    for min, avg, max in details: 
        select_range_dict = {}
        select_range_dict['min'] = min
        select_range_dict['avg'] = avg
        select_range_dict['max'] = max
        select_date_values_range.append(select_range_dict)

    return jsonify(select_date_values_range)

if __name__ == "__main__":
    app.run(debug=True)
