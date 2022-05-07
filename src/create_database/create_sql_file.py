# CSC 315
# Create SQL File

import csv

def create_sql_file():
    f = open("team4_db.sql", "w+")
    #drop database, create database, create tables
    f.write("CREATE TABLE METER(MeterName text, MeterID text, Type text, Unit text, PRIMARY KEY(MeterName));\n")
    f.write("CREATE TABLE COST(MeterName text, StartDate date, EndDate date, Amount float(2), PRIMARY KEY(MeterName, StartDate, EndDate), FOREIGN KEY (MeterName) REFERENCES METER(MeterName));\n")
    f.write("CREATE TABLE ENERGY(MeterName text, StartDate date, EndDate date, Amount integer, PRIMARY KEY(MeterName, StartDate, EndDate), FOREIGN KEY (MeterName) REFERENCES METER(MeterName));\n")

    #fill the METER table
    with open("meters.csv") as csvfile:
        meter_reader = csv.reader(csvfile)
        headers = next(meter_reader)
        for row in meter_reader:
            meter_id = row[2]
            meter_name = row[3]
            meter_type = row[4]
            meter_unit = row[5]
            f.write("INSERT INTO METER (MeterName, MeterID, Type, Unit) VALUES (" + "\'" + meter_name + "\'" + ", " + "\'" + meter_id + "\'" + ", " + "\'" + meter_type + "\'" + ", " + "\'" + meter_unit + "\'" + ");\n")

    #fill the COST and ENERGY tables
    with open("meter_entries.csv") as csvfile:
        meter_entry_reader = csv.reader(csvfile)
        headers = next(meter_entry_reader)
        for row in meter_entry_reader:

            meter_name = row[3]
            meter_StartDate = row[6]
            meter_EndDate = row[7]
            meter_cost_amount = row[11]
            meter_energy_amount = row[9]

            if meter_name == "Estimated Co-Gen Electric" or meter_name == "Fuel Oil Deliveries" or meter_name == "NG8 Error In Units":
                continue
            
            if meter_energy_amount == "Not Available":
                meter_energy_amount = "0"
            
            if meter_cost_amount == "Not Available":
                meter_cost_amount = "0"
        
            f.write("INSERT INTO COST (MeterName, StartDate, EndDate, Amount) VALUES (" + "\'" + meter_name + "\'" + ", " + "\'" + meter_StartDate + "\'" + ", " + "\'" + meter_EndDate + "\'" + ", " + meter_cost_amount + ");\n")
            f.write("INSERT INTO ENERGY (MeterName, StartDate, EndDate, Amount) VALUES (" + "\'" + meter_name + "\'" + ", " + "\'" + meter_StartDate + "\'" + ", " + "\'" + meter_EndDate + "\'" + ", " + meter_energy_amount + ");\n")

    #create view after filling tables with data
    f.write("CREATE VIEW ENERGY_COST AS SELECT ENERGY.MeterName, ENERGY.StartDate, ENERGY.EndDate, ENERGY.Amount AS EnergyAmount, COST.Amount AS CostAmount FROM ENERGY INNER JOIN COST ON ENERGY.MeterName = COST.MeterName AND ENERGY.StartDate=COST.StartDate AND ENERGY.EndDate = COST.EndDate;")


#call the function
create_sql_file()