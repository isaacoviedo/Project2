"""
Title :: ServerApp
Author:: Nicholas Hemstreet
Brief :: Unit Test for the webserver that pushes data to the database. Will check
basic conditions, such as thread safety, communicating with the interlinked data filter,
periodically pushing data, and receiving commands.

LICENSE:: This software is provided as is and can be used by any person who has
attained expressed permission of Nicholas Hemstreet (nhemstreet18@tamu.edu) any
unlicensed use in either classroom or in lecture will be met with angry emails.
"""



# Imports
import threading as th # Works with the sched portion
import time # For various temporally related events
import sched # used for scheduling the database nannying
import socket as sock # Used for communicating between the Server and Database
from DataFilter import DataFilter # Used to conver the raw sensing data into usable sensor data
import _mysql as db 

class ServerApp(object):
    """docstring for ServerApp."""
    db_host = ""
    db_user = ""
    db_name = ""
    db_pass = ""
    def __init__(self,dbConnection=True):
        
        super(ServerApp, self).__init__()
        self.sched = sched.scheduler(time.time,time.sleep)
        self.failed_queries = 0
        # Do initial setup to connect to the database
        self.dbConnection = dbConnection
        self.count_lock = th.Lock()
        self.kill_server = False
        self.counted_people = 0
        self.master_count = 0
        self.dataFilter = DataFilter()
        # If we want a connection to the dB we connect here
        if (self.dbConnection):
            # Connect to the server
            self.connectToDb()
            # Should be valid now

    def connectToDb(self):
        self.db_host = "database.cse.tamu.edu"
        self.db_name = "ratlidav"
        self.db_user = "ratlidav"
        self.db_pass = "ratlidav"
        try:
            # In an actual implementation this will be more complicated
            self.conn = db.connect(host=self.db_host,user=self.db_user,db=self.db_name,passwd=self.db_pass)
        except Exception:
            print("Could not connect to the database server")

    def _getQuery(self,timestamp,count):
        """
        Helper function to make the updateDatabase function look prettier
        """
        return "INSERT INTO People_Count_Data_Web_Server_Dev(Time_Stamp, Count) VALUES ({0},{1})".format(timestamp,count)
    def setCount(self,value):
        self.count_lock.acquire()
        self.counted_people = value
        self.count_lock.release()

    def getCount(self):
        self.count_lock.acquire()
        count = self.counted_people
        self.count_lock.release()
        return count

    def updateDatabase(self):
        """** There is no reason that **""" 
        # Add the number of people that have passed since our last reading
        # We are posting to the table:: People_Count_Web_Server_Dev with our artificial timestamp and the count
        count = self.getCount()
        self.setCount(0)
        self.dataFilter.clearData()
        self.conn.ping() # Double check that we are still connected, if not reconnect and lets get this show on the road
        timestamp = time.time()
        try: 
            self.conn.send_query(self._getQuery(timestamp,count))
        except Exception : 
            # If there is an error with our query we print the error and fail with this update
            print("SQL Failed to send... There was some error with creating the query")
            self.failed_queries += 1
            print("This makes {0} Failures".format(self.failed_queries))
        if (not self.conn.read_query_result() == None):
            print("There was an error INSIDE of the query.")
            self.failed_queries += 1
            print("This makes {0} Failures".format(self.failed_queries))
        # Clear the state of our MySQL Client so no exchange errors occur
        self.conn.store_result()
        print("UpdatedDatabase")

    def _serverNanny(self):
        """
        Handles scheduling and nannying the server
        """
        while(not self.kill_server):
            # Schedule our event in 900 s
            self.sched.enter(30,1,action=self.updateDatabase)
            self.sched.run()
        print ("Server connection is being terminated... Nothing else will be sent to the database")
        self.conn.close()

# Main thread handles the reading and writing to the server/ data filter
# The db h
    def start(self):
        # Start the individual threads and set some sort of schedule
        databaseNanny = th.Thread(target=self._serverNanny)
        databaseNanny.start()
        # MAIN APPLICATION LOOP
        while(1):
            # Handle data collection
            self.dataFilter.renewPersonata()
            # Update our local mutex count
            self.setCount(self.dataFilter.getData())
            #print(str(time.time()))
           # print("Updated Data")
            # Sleep so the sensor has time to do other things
            time.sleep(0.150)

if (__name__ == "__main__"):
    serv = ServerApp(dbConnection=True)
    serv.start()
