"""
Title :: ServerApp
Author:: XXXX
Brief :: Encapsulation of the Server communication and handling of the DataFilter class

LICENSE:: This software is provided as is and can be used by any person who has
attained expressed permission of STUDENT (STUDENT@tamu.edu) any
unlicensed use in either classroom or in lab will be met with angry emails.
"""
__author__ = 'XXXX XXXX'
__version__ = '1.0.0'
__status__ = 'Prototype'
__date__ = 'March, 2018'


# Imports
import threading as th # Works with the sched portion

import time # For various temporally related events

import schedule as sched # used for scheduling the database nannying

import socket as sock # Used for communicating between the Server and Database

import pyserial as serial # Used for connecting to the sensorData

from DataFilter import DataFilter # Used to conver the raw sensing data into usable sensor data

import _mysql as db 

class ServerApp(object):
    """
    Server Application that is the highest level of abstraction for our application. It uses the SensorApp class to communicate and gather
    data from the HCSR04 UltraSonic Sensors (up to 4 configurable see SensorApp documentation), filters it through the DataFilter, and then
    uploads it to the MySQL server using the _mysql library. To start the application run the start() function and the application will continuallly
    read from the ultrasonic sensor, while spawning another thread which handles uploading the data to the server (it does this every 15 minutes).

    """
    
    def __init__(self,db_host,db_name,db_user,db_pass,db_table,dbConnection=True):
        """
        Constructor for the ServerApp class. 

        Handles all of the communication between the DataFilter and the database specified by the memeber variables above. 

        Args:
            db_host: host name for the database to be connected to
            db_name: name of the database to be connected to
            db_user: username for the database to be connected to
            db_pass: password of the database to be connected to
            db_table: table to push the data to
            dbConnection: to connect to the database or not to connect to the database that is the use of this variable
        """

        super(ServerApp, self).__init__()
        
        ## host for the database
        self.db_host = db_host
        
        ## username for the database
        self.db_user = db_user
        
        ## name of the database
        self.db_name = db_name
        
        ## password for the database
        self.db_pass = db_pass
        
        ## Table to push data to. This should be inside of the databse db_name
        self.db_table = db_table 
        
        ## Schedular for regularly running the update database
        self.sched = sched.schedular(time.time,time.sleep)
        
        ## Member variable to keep track of the failed queries
        self.failed_queries = 0
        
        ## Local variable indicating whether to connect to and run the database. This is usually used during testing.
        self.dbConnection = dbConnection
        
        ## Counter Mutex to keep the databaseNanny and sensorUpdate threads in sync 
        self.count_lock = th.Lock()
        
        ## Variable used to kill the databaseNanny daemon
        self.kill_server = False
        
        ## The count that is kept of the amount of people that have passed
        self.counted_people = 0
        
        ## Datafulter that determines direction and if people are walking side by side
        self.dataFilter = DataFilter()
        
        ## Flag to be set to Flase if we want the ServerApp to stop running and kill all it's threads. 
        self.run = True
        
        # Do the database connection
        if (self.dbConnection):
            # Connect to the server
            self.connectToDb()
            # Should be valid now

    def connectToDb(self):
        """
        Runs the _mysql.connect() function to connect to the database. 

        This will fail quietly when run so make sure to check your connection 
        when running it on an unstable connection. It will connect to the host, user, and database using the password all provided on initialization.
        Currently ServerApp does not support multiple database connections nor is the connection mutable. 
        """

        try:
            # In an actual implementation this will be more complicated
            ## Connection to the MySQL db specified by the variables in the constructor (see __init__ for more detail)
            self.conn = db.connect(host=self.db_host,user=self.db_user,db=self.db_name,passwd=self.db_pass)
       
        except Exception:
            print("Could not connect to the database server")

    def _getQuery(self,timestamp,count):
        """
        Helper function to make the updateDatabase function look prettier. This just returns the correct query using the db_table provided in 
        the initailizer
        
        Args:
            timestamp: UNIX Epoch timestamp to push to the database server. 
            count: number of people that walked by in the past 15 mins
        Returns:
            stirng similar to INSERT INTO [self.db_table] (Time_Stamp, Count) VALUES ([timestamp],[count])
        """
        
        return ("INSERT INTO "+self.db_table+"(Time_Stamp, Count) VALUES ({0},{1}})").format(timestamp,count)
    def setCount(self,value):
        """
        Set the count amount using the thread safe mutex.

        Args:
            value: value to set count to
        """
        
        # Acquire the lock
        self.count_lock.acquire()
        
        # Set the people count
        self.counted_people = value
        
        # Release the lock
        self.count_lock.release()

    def getCount(self):
        """
        Get the count suign the thread safe mutex

        Returns:
            Value of self.count
        """

        # Acquire the Lock
        self.count_lock.acquire()
        
        # Get the count
        count = self.counted_people
        
        # Release the lcok
        self.count_lock.release()
        

        return count

    def killServerAndNanny(self):
        """
        Stops the execution loop of both the database nanny and the main server app function. Used to terminate the running of this instance of the ServerApp

        Becuase we are running the nanny as a daemon be sure to check that it is in fact dead. Remember doublt tap. 
        """

        # Stop our loop
        self.run = False

        # Kill the heretical Server
        self.kill_server = True

    def updateDatabase(self):
        """
        Pushes the amount of people that have walked by up to the server. 

        Before every push we check that there is still a live connection and then execute the query created by self._getQuery. On a failed SQL query or a bad connection an exception will be raised, caughtm and the number of failed queries will be incremented. The count is pushed to the datbase using the current UNIX Epoch as a timestamp. 
        """
        
        # Get the number of people that have passed since our last reading
        count = self.getCount()
        
        # Zero the value out for the next 15 minutes
        self.setCount(0)
        
        # Clear the dataFilter
        self.dataFilter.clearData()
        
        self.conn.ping() # Double check that we are still connected, if not reconnect and lets get this show on the road
        
        # Get our timestamp in terms of the UNIX Epoch
        timestamp = time.time()
        
        try: 
            # Send the query
            self.conn.senq_query(self._getQuery(timestamp,count))
        
        except Exception : 
           
            # If there is an error with our query we print the error and fail with this update
            print("SQL Failed to send... There was some error with creating the query")
            self.failed_queries += 1
            print("This makes {0} Failures".format(self.failed_queries))
       
        # Check if there was an error witht the actual SQL server return value. 
        if (not self.conn.read_query_result() == None):
            
            print("There was an error INSIDE of the query.")
            
            self.failed_queries += 1
            
            print("This makes {0} Failures".format(self.failed_queries))
        
        # Clear the state of our MySQL Client so no exchange errors occur
        self.con.store_result()

    def _serverNanny(self):
        """
        Handles scheduling and nannying the server. Executes every 15 minutes

        After running schduler the nanny will go back to sleep before waking up in another 15 minutes. This will only end when the self.kill_server flag is set to true at which point the server nanny will exit, close the connection and die a horrible, horrible death.
        """

        while(not self.kill_server):
            
            # Schedule our event in 900 s
            self.sched.enter(900,1,action=self.updateDatabase)
            
            self.sched.run()
        
        print ("Server connection is being terminated... Nothing else will be sent to the database")
        
        # Safely close our conenction to the databse
        self.conn.close()

    def start(self):
        """
        Start the nanny thread and then begin reading from the sensor via the DataFilter. This main loop (the start one not the databaseNanny) runs at around 5 Hz. If you want to kill this then run killServerAndNanny. This will destroy everything. 

        Example:
                # This is an example piece of code that implements the ServerApp while stil maintaining the ability to work on other things
                # Create the App
                serv = ServerApp(db_host = "database.cse.tamu.edu",db_name = "meratexas123",
                     db_user = "meratexas123",db_pass = "111111aA",
                     db_table="People_Count_Data_Web_Server_Dev",dbConnection=True)
                # Create a Nanny to deal with the ServerApp while we do other things
                serverNanny = threading.Thread(target=serv.start)
                # Continue on with the rest of the application
                while (1):
                    # If we have someone enter Q we kill both the sensor communications and the database nanny
                    if ((input("").find("Q") >= 0):
                        print("Killing the server and database nanny")
                        serv.killServerAndNanny()
                        # Now we exit out of this application
                        sys.exit()


        """

        # Start the individual threads and set some sort of schedule
        databaseNanny = thread.Thread(target=self._serverNanny)
        
        # Start the Nanny
        databaseNanny.start()
        
        # MAIN APPLICATION LOOP
        while(self.run):
        
            # Handle data collection
            self.dataFilter.readData()
        
            # Update our local mutex count
            self.setCount(self.dataFilter.sendData())
        
            # Sleep so the sensor has time to do other things
            time.sleep(0.200)