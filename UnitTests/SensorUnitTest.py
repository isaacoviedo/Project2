'''
Unit Test for the SensorApp class' interaction with the Arduino.

Reads data for approximately 60 seconds and exports to logger.csv. The user should then check that the values mentioned there match up with the actions
taken during the testing time. Given more time and resources we could rig up a forwarding service that properly tested these values, but this works for right
now.

'''

# IMPORTS
from SensorApp import SensorApp

if (__name__ == "__main__"):
    
    # Create .csv file to store distance values from sensor
    logFile = open('logger.csv',"w")
    logFile.write("Timestamp 1, Sens 1 Reading, Timestamp 2, Sens 2 Reading\n")
    
    print("Application Starting")
    
    # Instantiate SensorApp object and configure appropriately
    sens = SensorApp("COM5",250000,5,[2,5],[9,12])
    sens.configure_ard()
    
    # Run for approximately 60 seconds
    i = 0
    while(i < 240):
        resp = sens.readFromSensor(1)
        logFile.write(str(resp[0][0][0]) + "," + str(resp[0][0][1]) + "," + str(resp[1][0][0]) + "," + str(resp[1][0][1])+ "\n")
        time.sleep(0.250)
        i += 1
    
    logFile.close()
    print("Ending")
    # END OF UNIT TEST