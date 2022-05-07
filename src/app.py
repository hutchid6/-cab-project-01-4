#! /usr/bin/python3

#Contributors: Bret Elphick, Dalton Hutchinson, Jimmy Fay
#Project Name - CSC 315: Energy Demand Tool
#Project Description - Tool extracts data from database, creates a table, creates charts, and creates stat cards 
#File Name - app.py
#File Description - File extracts data, formats data, and serves webpages 

import psycopg2
from config import config
from flask import Flask, render_template, request
import math
from datetime import datetime

# Connect to the PostgreSQL database server
def connect(query):
    conn = None
    try:
        # read connection parameters
        params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the %s database...' % (params['database']))
        conn = psycopg2.connect(**params)
        print('Connected.')
      
        # create a cursor
        cur = conn.cursor()
        
        # execute a query using fetchall()
        cur.execute(query)
        rows = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
    # return the query result from fetchall()
    return rows

# app.py
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# serve form web page
@app.route("/", methods = ['GET'])
def form():
    meters = connect("select distinct metername from meter;")
    for i, s in enumerate(meters):
        meters[i] = s[0]
    return render_template('my-form.html', meternames = meters)

# handle venue POST and serve result web page
@app.route('/result', methods=['POST'])
def result():

    #if a date field was not filled in reload the page
    if request.form["startdate"] == "" or request.form["enddate"] == "":
        return form()
    #if the end date is before the start date reload the page
    if datetime.strptime(request.form["startdate"], "%Y-%m-%d") > datetime.strptime(request.form["enddate"], "%Y-%m-%d"):
        return form()

    #headers for the table
    heads = ["Start Date", "End Date", "Energy Amount", "Cost Amount"]
    
    #psql queries
    #get table data using energy_cost view
    table = connect("select energy_cost.startdate, energy_cost.enddate, energy_cost.energyamount, energy_cost.costamount from energy_cost where energy_cost.metername='"+ request.form['metername'] + "' and energy_cost.startdate>=(select energy.startdate from energy where metername='" + request.form['metername'] + "' order by abs(energy.startdate - '" + request.form['startdate'] + "') limit 1) and energy_cost.enddate<=(select energy.enddate from energy where metername='" + request.form['metername'] + "' order by abs(energy.enddate - '" + request.form['enddate'] + "') limit 1);")
    #get all cost amounts for inputted meter over inputted time range
    cost_amounts = connect("select amount from cost where metername='"+ request.form['metername'] + "' and startdate>=(select cost.startdate from cost where metername='" + request.form['metername'] + "' order by abs(cost.startdate - '" + request.form['startdate'] + "') limit 1) and enddate<=(select cost.enddate from cost where metername='" + request.form['metername'] + "' order by abs(cost.enddate - '" + request.form['enddate'] + "') limit 1);")
    #get all energy amounts for the inputted meter over the inputted time range
    energy_amounts = connect("select amount from energy where metername='" + request.form["metername"] + "' and startdate >=(select energy.startdate from energy where metername='" + request.form["metername"] + "' order by abs(energy.startdate - '" + request.form["startdate"] + "') limit 1) and enddate<=(select energy.enddate from energy where metername='" + request.form["metername"] + "' order by abs(energy.enddate - '" + request.form["enddate"] + "') limit 1);")
    #get the start and end dates for all meter entries in the inputted time range
    start_end_dates = connect("select startdate, enddate from energy where metername='" + request.form["metername"] + "' and startdate >=(select energy.startdate from energy where metername='" + request.form["metername"] + "' order by abs(energy.startdate - '" + request.form["startdate"] + "') limit 1) and enddate<=(select energy.enddate from energy where metername='" + request.form["metername"] + "' order by abs(energy.enddate - '" + request.form["enddate"] + "') limit 1);")
    #get the type and unit of inputted meter
    type_unit = connect("select type, unit from meter where metername = '" + request.form["metername"] + "';")
    #get the average cost for the inputted meter over the inputted time range
    avg_cost = connect("select avg(amount) from cost where metername='"+ request.form['metername'] + "' and startdate>=(select cost.startdate from cost where metername='" + request.form['metername'] + "' order by abs(cost.startdate - '" + request.form['startdate'] + "') limit 1) and enddate<=(select cost.enddate from cost where metername='" + request.form['metername'] + "' order by abs(cost.enddate - '" + request.form['enddate'] + "') limit 1);")
    #get the sum cost for the inputted meter over the inputted time range
    sum_cost = connect("select sum(amount) from cost where metername='"+ request.form['metername'] + "' and startdate>=(select cost.startdate from cost where metername='" + request.form['metername'] + "' order by abs(cost.startdate - '" + request.form['startdate'] + "') limit 1) and enddate<=(select cost.enddate from cost where metername='" + request.form['metername'] + "' order by abs(cost.enddate - '" + request.form['enddate'] + "') limit 1);")
    #get the sum energy for the inputted meter over the inputted time range
    sum_energy = connect("select sum(amount) from energy where metername='" + request.form["metername"] + "' and startdate >=(select energy.startdate from energy where metername='" + request.form["metername"] + "' order by abs(energy.startdate - '" + request.form["startdate"] + "') limit 1) and enddate<=(select energy.enddate from energy where metername='" + request.form["metername"] + "' order by abs(energy.enddate - '" + request.form["enddate"] + "') limit 1);")
    #get the average energy for the inputted meter over the inputted time range
    avg_energy = connect("select avg(amount) from energy where metername='" + request.form["metername"] + "' and startdate >=(select energy.startdate from energy where metername='" + request.form["metername"] + "' order by abs(energy.startdate - '" + request.form["startdate"] + "') limit 1) and enddate<=(select energy.enddate from energy where metername='" + request.form["metername"] + "' order by abs(energy.enddate - '" + request.form["enddate"] + "') limit 1);")
    
    #select the first item in each returned tuple
    for i, s in enumerate(cost_amounts):
        cost_amounts[i] = s[0]
    for i, s in enumerate(energy_amounts):
        energy_amounts[i] = s[0]

    #create the labels for the graphs
    start = start_end_dates[0][0]
    end = start_end_dates[-1][1]
    for i, s in enumerate(start_end_dates):
        start_end_dates[i] = str(s[0]) + ":" + str(s[1])

    #calculate average co2e using average energy amount
    co2e = calculate_co2e(round(avg_energy[0][0],2), type_unit[0][1])
    
    #serve the results page
    return render_template('my-result.html', table=table, heads=heads, metername=request.form['metername'], startdate=start, enddate=end, labels=start_end_dates, cost_amounts=cost_amounts, energy_amounts=energy_amounts, type=type_unit[0][0], unit=type_unit[0][1], avg_cost=round(avg_cost[0][0], 2), sum_cost= round(sum_cost[0][0], 2), avg_energy=round(avg_energy[0][0], 2), sum_energy= round(sum_energy[0][0], 0), co2e=co2e)

def calculate_co2e(amount, unit):
    #all conversion factors were found at carbonfund.org
    amount = float(amount)
    if (unit == "kWh (thousand Watt-hours)"):
        #use the kwh to co2e conversion factor
        return round(amount * 0.000429, 2)
        pass
    elif (unit == "therms"):
        #convert to kwh
        amount = amount * 29.3001
        #use the kwh to co2e conversion factor
        return round(amount * 0.000429, 2)
        pass
    else:
        #use the ccf to co2e conversion factor
        return round(amount * .00531, 2)


if __name__ == '__main__':
    app.run(debug = True)
