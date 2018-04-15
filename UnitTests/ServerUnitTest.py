"""
Title :: ServerUnitTest
Author:: XXXXX
Brief :: Unit Test for the webserver that pushes data to the database. Will check
basic conditions, such as thread safety, communicating with the interlinked data filter,
periodically pushing data, and receiving commands.
LICENSE:: This software is provided as is and can be used by any person who has
attained expressed permission of Nicholas Hemstreet (nhemstreet18@tamu.edu) any
unlicensed use in either classroom or in lecture will be met with angry emails.
"""


"""
### THIS ONLY TESTS THE SERVERS ABILITY TO CONNECT TO THE DB, PUSH DATA, AND CONNECT TO THE
SENSOR
DATA SENT TO THE DATAASE NEEDS TO BE MANUALLY CHECKED FOR NOW COMPLAIN TO MANAGEMENT
IF YOU WNAT SOMETHING DIFFERENT
"""

# Imports
import threading
import ServerApp
import sockets
import random as rand
import pyserial as serial
import time


if (__name__ == "__main__"):
     serv = ServerApp(db_host = "database.cse.tamu.edu",db_name = "meratexas123",
                     db_user = "meratexas123",db_pass = "111111aA",
                     db_table="People_Count_Data_Web_Server_Dev",dbConnection=True)
     
     # Send a bunch of random data to the server and see if it works
     for i in range(0,400,10):
        
        serv.setCount(i)
        
        serv.updateDatabase()
        
        time.sleep(1)
     
     input("Check the PHPMyAdmin page and make sure the data is correct")
     
     # Repeat again to check if the connection is still live after a long time
     time.sleep(20)

     # Repeat the above test with higher values and check again
     for i in range(0,10000,100):
        
        serv.setCount(i)
        
        serv.updateDatabase()
        
        time.sleep(1)
     
     input("Check the PHPMyAdmin page and make sure the data is correct")

    # If everything went properly then we should end up with 138 entries inside of
    # the datbase.
     
