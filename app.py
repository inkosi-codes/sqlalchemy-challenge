import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify, render_template

#-----------------------------------------------#
#       Create a connection to the Database     #
#-----------------------------------------------#
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#-----------------------------------------------#
#              Initialize the app               #
#-----------------------------------------------#
app = Flask(__name__)

#-----------------------------------------------#
#         Create the session globally           #
#-----------------------------------------------#
session = Session(engine)

#-----------------------------------------------#
#              Global Variables                 #
#-----------------------------------------------#
yeardate = (dt.datetime(2017,8,23) - dt.timedelta(days=1*365)).strftime("%Y-%m-%d")

#-----------------------------------------------#
#                   Routes                      # 
#-----------------------------------------------#

@app.route("/")
def routes():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            if (rule.rule != '/'):
                routes.append(rule.rule)
    return render_template("index.html", data=routes)


@app.route("/api/v1.0/precipitation")
def precipitation():

    #Create a list to hold finished dictionary
    precip_list = []

    #Query the Database and store results
    for i in session.query(Measurement.date, Measurement.prcp).all():
        entry = {i[0]: i[1]}
        precip_list.append(entry)
    
    #Close out the current thread
    session.close()

    #Jsonify and Return the rsults to the frontend
    return jsonify(precip_list)


@app.route("/api/v1.0/stations")
def stations():

    #Query the Database and store results
    results = session.query(Station.station).\
                 order_by(Station.station).all()

    #Close out the current thread
    session.close()

    #Jsonify and Return the rsults to the frontend
    return jsonify(list(np.ravel(results)))


@app.route("/api/v1.0/tobs")
def tobs():

    #Create a list to hold finished dictionary
    tobs_list = []

    #Create query to find most active station and store in variable
    active_station = session.query(Measurement.station, func.count(Measurement.station).label('cnt')).\
        group_by(Measurement.station).order_by(desc('cnt')).first()

    #Query the Database and store results
    for i in session.query(Measurement.date,  Measurement.tobs,Measurement.prcp).\
                filter(Measurement.date >= yeardate).\
                filter(Measurement.station == active_station[0]).\
                order_by(Measurement.date).all():
        item = {'Date': i[0], 'Tobs': i[1], 'Precip': i[2]}
        tobs_list.append(item)

    #Close out the current thread
    session.close()

    #Jsonify and Return the rsults to the frontend
    return jsonify(tobs_list)

    
@app.route("/api/v1.0/<start_date>")
def Start_date(start_date):

    # Perform the dynamic query based on start date and store the results
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()


    #Build dataset into a dictionary
    startdate_dict = {}
    startdate_dict["temperature_min"] = results[0][0]
    startdate_dict["temperature_max"] = results[0][1]
    startdate_dict["temperature_avg"] = round(results[0][2],2)
    
    #Close out the current thread
    session.close()

    #Jsonify and Return the rsults to the frontend
    return jsonify(startdate_dict)

@app.route("/api/v1.0/<start_date>/<end_date>")
def Start_end_date(start_date, end_date):
    
    # Perform the dynamic query based on start date and store the results
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

  
    #Build dataset into a dictionary
    result_dict = {}
    result_dict["min_temp"] = results[0][0]
    result_dict["avg_temp"] = round(results[0][1],2)
    result_dict["max_temp"] = results[0][2]
    
    #Close out the current thread
    session.close()

    #Jsonify and Return the rsults to the frontend
    return jsonify(result_dict)


if __name__ == '__main__':
    app.run(debug=True)