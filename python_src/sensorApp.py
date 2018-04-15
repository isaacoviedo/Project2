# Python implementation of the Sonar Ranging Application

__author__ = 'Nicholas Hemstreet'
__version__ = '0.1.0'
__status__ = 'Prototype'
__date__ = 'March, 2018'


debug = True

from datetime import datetime # For getting the current time
import time # so we have access to the sleep function
import sys # For aborting
import binascii
import serial
import csv
class SensorApp(object):
    """
    Implementation talking to the ranging sensor.
    Encaspulates the configuration and communication with the
    sensor. 
    """
    def __init__(self, arduino_port,baudrate,update_rate,
                 trigger_pins,echo_pins,logData = False):
        super(SensorApp, self).__init__()
        self.arduino_port = arduino_port
        self.baudrate = baudrate
        # Should now have a serial socket
        self.sock = serial.Serial(self.arduino_port,self.baudrate)
        self.update_rate = update_rate
        if (not (len(trigger_pins) == len(echo_pins)) and not len(triggerPin) == 0):
            print("Improper declarations.")
            print("Need the same amount of trigger and echo pins")
            sys.exit()
        self.trigger_pins = trigger_pins
        self.echo_pins = echo_pins
        self.last_recorded_readings = []
        self.log_data = logData
    def configure_ard(self):
        """
         Configure the Arduino
        """
        print("User should restart Arduino now")
        print("Once Restarted press any button to configure the Arduino")
        a = input();
        # Now we make the configuration
        confString = "CON" + str(self.update_rate) + ","
        ech_str = "ECH,"
        trig_str = "TRI,"
        for i in range(0,len(self.trigger_pins)):
            # Build the two strings
            ech_str += str(self.echo_pins[i]) + ","
            trig_str += str(self.trigger_pins[i]) + ","
        confString += trig_str
        confString += ech_str
        print(confString)
        self.sock.write((confString + "\n").encode())
        
        resp_str = self.readFromSerial(self.sock.in_waiting)
        while(resp_str.find("SUC") == -1):
            self.sendToSerial(confString+"\n")
            time.sleep(1)
            resp_str = self.readFromSerial(self.sock.in_waiting)
        print("SUCCESS")
        # should get a response from the socket
        # # Will check here in a second
        # print(binascii.b2a_qp(self.sock.readline()))
        # print(binascii.b2a_qp(self.sock.readline()))

    def readFromSerial(self,msg_length):
        """
        Encapsulates the actual read and conversion to ASCII to
        make this more digestable.
        """
        if (msg_length > self.sock.in_waiting):
            retval = str(self.sock.read(self.sock.in_waiting))
            return retval[2:len(retval)-1]
        else:
            retval =  str(self.sock.read(msg_length))
            return retval[2:len(retval)-1]
    
    def sendToSerial(self,msg):
        if (type(msg) == type("")):
            return self.sock.write(msg.encode())
        else:
            return None

    def readFromSensor(self, nbrReadings=5):
        """
        \returns number configured arrays of tuples (timestamp, reading)
        """
        # Send the REQ command
        if (nbrReadings > 10):
            nbrReadings = 10

        readings = []
        for i in range(0,len(self.echo_pins)):
            readings.append([])
        req_str = "REQ" + str(nbrReadings) + ",\n"
       # print("Message Sent:: " + req_str)
        self.sendToSerial(req_str)
        time.sleep(0.2)
        # Now we need to parse a
        # response of the form REP + + + +
        # where + = a reading

        # Format == REP5,1.0,1,2.0,2,3.0,3,4.0,4,5.0,5
       # print("Reading from socket")
        response_found = False
        if (not self.sock.in_waiting):
            return [[(999999999,40000)],[(999999999,40000)]]

        resp_str = self.readFromSerial(self.sock.in_waiting)
        while (resp_str.find("REP") == -1 and self.sock.in_waiting):
            self.sendToSerial(req_str)
            time.sleep(0.5)
            print("Reading More")
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
                  #  print(resp_str)
                else:
                    # If there is a comma we know that from
                    # 0 to the index is the number
                    timestamp = resp_str[resp_str.find("(")+1:resp_str.find(",")]
                    reading   = resp_str[resp_str.find(",")+1:resp_str.find(")")]
                    resp_str = resp_str[resp_str.find(")")+1:] # Reset the response string
                    # Convert the value to a string and add it our array
                   # print ("Timestamp :: " + timestamp + " Reading:: " + reading)
                    readings[sensor_val].append((int(timestamp),float(reading)))
                    if (readings_per_sensor == 1):
                        sensor_val += 1
                        readings_per_sensor = nbrReadings
                    else:
                        readings_per_sensor -= 1
                    nbr_commas -= 1
        except Exception:
            if (self.sock.in_waiting == 0):
                print ("Failure")
                return [[(999999999,40000)],[(999999999,40000)]]
            print("Recurse")
            return self.readFromSensor(nbrReadings)
        #print("Success")
        return readings


def printPrettyResponse(resp):
    for i in resp:
        for val in i:
            print ("Timestamp:: " + str(val[0]) + " Reading:: " + str(val[1]))


# if (__name__ == "__main__"):
#     """
#     Function to actually run the SensorApplication
#     """
#     logFile = open('logger.csv',"w")
#     logFile.write("Timestamp 1, Sens 1 Reading, Timestamp 2, Sens 2 Reading\n")

#     print("Application Starting")
#     sens = SensorApp("COM5",250000,5,[2,5],[9,12])
#     sens.configure_ard()
#     if (debug):
#         while(1):
#             resp = sens.readFromSensor(1)
#             logFile.write(str(resp[0][0][0]) + "," + str(resp[0][0][1]) + "," + str(resp[1][0][0]) + "," + str(resp[1][0][1])+ "\n")
#             printPrettyResponse(resp)
#             time.sleep(0.250)
#     # Now we can read/response with the sensors
#     logFile.close()
#     print(str(sens.readFromSensor()))
#     print("Ending")
#     # Should not execute past this point
