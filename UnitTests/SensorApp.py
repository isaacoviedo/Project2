"""
Title :: SensorApp
Author:: XXXX
Brief :: Implementation and encapsulation of the Arduino/Sensor communication for the project

LICENSE:: This software is provided as is and can be used by any person who has
attained expressed permission of STUDENT (STUDENT@tamu.edu) any
unlicensed use in either classroom or in lab will be met with angry emails.
"""

__author__ = 'XXXX XXXX'
__version__ = '0.1.0'
__status__ = 'Prototype'
__date__ = 'March, 2018'


from datetime import datetime # For getting the current time

import time # so we have access to the sleep function

import sys # For aborting

import binascii

import serial

import csv


class SensorApp(object):
    """
    Implementation talking to the ranging sensor.

    Encaspulates the configuration and communication with the sensor using custom configuration protocol. This class needs to be used in conjunction with the firmware held inside of the Arduino directory
    """
    
    def __init__(self, arduino_port,baudrate,update_rate,trigger_pins,echo_pins):
        """
        Initializes the SensorApp with the given arduino_port and the baudrate on that port. 

        Args:
            arduino_port: port to communicate to the arduino over
            baudrate: baudrate of the arduino_port, for our application we set it to 250kHz, but if you change the the baudrate in the firmware you need to change this aswell
            update_rate: update rate that the arduino will be set to
            trigger_pins:  An array of the trigger pins that is the same length as the echo_pins
            echo_pins: An array of the echo_pins that is the same length as the trigger_pins
        """

        super(SensorApp, self).__init__()
        
        ## Port for the Arduino to connect to
        self.arduino_port = arduino_port
        
        ## Baudrate of the arduino_port, should be 250000
        self.baudrate = baudrate
        
        ## Serial Socket created to communicate with the arduino over the arduino_port
        self.sock = serial.Serial(self.arduino_port,self.baudrate)
        
        ## Specified update_rate for the arduino
        self.update_rate = update_rate
        
        # Check if we have a good setting
        if (not (len(trigger_pins) == len(echo_pins)) and not len(triggerPin) == 0):
            print("Improper declarations.")
            print("Need the same amount of trigger and echo pins")
            sys.exit()
        
        ## Pins for triggering the ultrasonic sensor
        self.trigger_pins = trigger_pins
        
        ## Pins for the echo signal on the ultrasonic sensor
        self.echo_pins = echo_pins

    def configure_ard(self):
        """
         Configures the arduino with the number of trigger and echo pins as well as the update rate specified in the initialization of the sensorApp class. 

         We create the configuration string, send it, and then wait for the SUCC key to be returned which indicates that the Arduino has been properly configured. There is no error checking here and it is intentionally made so that the program hangs. If no configuration comes back the sensor should not be run. 
        """
        
        # Now we make the configuration
        confString = "CON" + str(self.update_rate) + ","
        
        ech_str = "ECH,"
        
        trig_str = "TRI,"
        
        # Build the echo and trigger configuration strings
        for i in range(0,len(self.trigger_pins)):
            # Build the two strings
            ech_str += str(self.echo_pins[i]) + ","
            trig_str += str(self.trigger_pins[i]) + ","
        

        # Add the trig_String and echo_string to the configuration string
        confString += trig_str
        confString += ech_str
        
        # Write the configuration string to the socket
        self.sock.write((confString + "\n").encode())
        
        # Read the response from the serial
        resp_str = self.readFromSerial(self.sock.in_waiting)
        
        # Wait until we get success from the socket
        while(resp_str.find("SUC") == -1):
            self.sendToSerial(confString+"\n")
            time.sleep(0.5)
            resp_str = self.readFromSerial(self.sock.in_waiting)

        # Inform the user that we succeeded
        print("SUCCESS")

    def readFromSerial(self,msg_length):
        """
        Encapsulates the reading from the serial socket and conversion to ASCII to make this more digestable.

        Args:
            msg_length: length of the message to read from the buffer. If the requested message length is longer than the currently available data then only the currently available data is returns

        Returns:
            An ascii encoded string of the data on the bus of length msg_length or sock.in_waiting
        """

        # Check to see if the message length is too large
        if (msg_length > self.sock.in_waiting):
            # Read the full amount waiting in the socket if msg_length is greedy
            retval = str(self.sock.read(self.sock.in_waiting))
            return retval[2:len(retval)-1]

        # Read the msg_length if it is less than the buffer
        else:
            retval =  str(self.sock.read(msg_length))
            return retval[2:len(retval)-1]
    
    def sendToSerial(self,msg):
        """
        Helper function to convert the characters to ascii encoding so that the Arduino can understand them. If the msg is of type string then this function will write it to the serial socket and return the number of bytes written otherwise it will return the None type
        
        Args:
            msg: msg to be sent over the serial socket

        Returns:
            None if the message is not of type string or the amount of characters written to the socket
        """

        # Make sure that the type is correct
        if (type(msg) == type("")):
            # If it is a string send the message
            return self.sock.write(msg.encode())
        else:
            # Otehrwise return NULL
            return None

    def readFromSensor(self, nbrReadings=5):
        """
        Reads the number of readings specified by nbrReadings from the sensor. Returns an array that is of the following format:: [[Sensor][Sensor][Sensor]]  Where Sensor is an array of tuples which contain the timestamps at which they where taken and the readings [(TS,RD),(TS,RD),(TS,RD)]. So an exampe of a returned value would be [[(123,456)],[(456,323)],[(765,345)]] Accessign the readings of Sensor one would then be returnVAlue[0][0][1] Where the first 0 is the sensor, the second thr reading and the last index should be 0 or 1 where 0 is the timestamp and 1 is the reading. 

        If you are interested in the format of the communication protocol you need to look at the top of the page or look inside of the documentation for the firmware where you can find the back and forth protocol laid out for you. If the value returned from the sensor is erroneous or there is a bad sync on the socket we will return a fasle value of:: [[(999999999,40000)],[(999999999,40000)]] whcih will be filtered out by our dataFilter. If you need to double check this value just check if the returned reading is over the max of the sensor which is 800. 


        Args:
            nbrReadings: number of readings to be returned by the sensor

        Returns:
            An array of array of tuples where the tuples are of type (Timestamp, Reading) and the array indexes are Sensor and reading number in that order or in the case of failure [[(999999999,40000)],[(999999999,40000)]]
        """
        
        # Send the REQ command
        if (nbrReadings > 10):
            nbrReadings = 10

        # The readings array
        readings = []


        for i in range(0,len(self.echo_pins)):
            readings.append([])
        req_str = "REQ" + str(nbrReadings) + ",\n"
       # print("Message Sent:: " + req_str)
        self.sendToSerial(req_str)
        # Now we need to parse a
        # response of the form REP + + + +
        # where + = a reading

        # Format == REP5,1.0,1,2.0,2,3.0,3,4.0,4,5.0,5

        response_found = False
        resp_str = self.readFromSerial(self.sock.in_waiting)
        while (resp_str.find("REP") == -1 and self.sock.in_waiting):
            resp_str += self.readFromSerial(self.sock.in_waiting)
        
        resp_str  = resp_str[resp_str.find("REP")+3:]

       
        # Cut out any extra amount of data
        nbr_commas = len(self.echo_pins)*nbrReadings
        sensor_val = 0 # index of the sensor we are reading from
        readings_per_sensor = nbrReadings
        # Get each one our pieces pof Data
        try: 

            while (nbr_commas > 0):
                
                if (resp_str.find(")") == -1):
                    resp_str += self.readFromSerial(self.sock.in_waiting)
                
                else:
                    # If there is a comma we know that from
                    # 0 to the index is the number
                    timestamp = resp_str[resp_str.find("(")+1:resp_str.find(",")]
                    
                    # Get the reading
                    reading   = resp_str[resp_str.find(",")+1:resp_str.find(")")]
                    
                    # Find the end of the repsonse string
                    resp_str = resp_str[resp_str.find(")")+1:] # Reset the response string
                    
                    # Convert the value to from a string and add it to the array
                    readings[sensor_val].append((int(timestamp),float(reading)))
                    
                    # Handle our incrementation
                    if (readings_per_sensor == 1):
                        # If we have only 1 reading left we move to the next sensor
                        sensor_val += 1

                        readings_per_sensor = nbrReadings
                    
                    else:
                        readings_per_sensor -= 1
                    
                    nbr_commas -= 1
        
        except Exception:
            
            # If there is a Socket exception where we either are trying to read from a nulled port or there is an issue with
            # the buffer on the socket return our defuault case
            if (self.sock.in_waiting == 0):
                return [[(999999999,40000)],[(999999999,40000)]]

            # Return the default case
            return self.readFromSensor(nbrReadings)
        
        return readings


    def printPrettyResponse(self,resp):
        """
        Helper function for debugging. Prints better looking responses that make it easier to read  the data

        """

        # Loop through each sensor
        for i in resp:

            # Loop through each value in the readings
            for val in i:
                print ("Timestamp:: " + str(val[0]) + " Reading:: " + str(val[1]))
