"""
Title :: demo
Author:: XXXX
Brief :: File used for demonstrating the use of ServerApp, DataFilter, and the SensorApp classes. 

LICENSE:: This software is provided as is and can be used by any person who has
attained expressed permission of STUDENT (STUDENT@tamu.edu) any
unlicensed use in either classroom or in lab will be met with angry emails.
"""

__author__ = 'XXXX XXXX'
__version__ = '1.0.0'
__status__ = 'Prototype'
__date__ = 'March, 2018'

# Import the Server App 
from ServerApp import *

# Import threading so the server can work in the backgroun
import threading

# Import sys so we can kill on exit
import sys


"""
Main loop for demo. Demonstrates creating the server, communicating with the database, and running other processes while the server runs in the background
"""
if (__name__ == "__main__"):

    # Create the server app
    serv = ServerApp(db_host = "database.cse.tamu.edu",db_name = "meratexas123",
    				 db_user = "meratexas123",db_pass = "111111aA",
    				 db_table="People_Count_Data_Web_Server_Dev",dbConnection=True)
    
    # Create the ServerNanny
    serv.start()

    