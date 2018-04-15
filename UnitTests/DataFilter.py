"""
LICENSE:: This software is provided as is and can be used by any person who has
attained expressed permission of STUDENT (STUDENT@tamu.edu) any
unlicensed use in either classroom or in lab will be met with angry emails.
"""

__author__ = "XXXX XXXX"
__version__ = "1.0"
__status__ = "Prototype"
__date__ = "March 31, 2018"




"""@package DataFilter
The rationale behind the implementation is that if an individual walks through a sensor, we expect to read a similar distance value in the other sensor within a relatively 
small timeframe. We use 'expectation buffers' to keep track of our expectations. If we do not read a distance value we expect within a given timeframe, then we know something 
is awry. We do not have all the information, so we need to make judgement calls based on what we do know. We keep track of various occurrences while a value exists in either 
expectation buffer to better help us make reasonable judgements to discern the direction and validity of measured data.
"""

# IMPORTS
from SensorApp import SensorApp
from collections import deque
import time

class DataFilter:
    """
    DataFilter instantiates SensorApp and processes distance values to determine the number of people walking in one direction when traffic is potentially bidirectional. 
    The DataFilter class itself is instantiated within the ServerApp class.
    """
    
    def __init__(self):
        """
        Instantiates SensorApp object and sets constants as specified. Calibrates environment noise.
        """
        
    # VALUES
        ## Object's local count for number of pedestrians
        self.peopleCounted = 0
        
        ## The number of readings we want from the sensor each cycle
        self.numReadings = 1

    # STRUCTURES
        ## Initializing SensorApp object
        self.sensor = SensorApp( "COM5",250000,5,[2,5],[9,12] )
        self.sensor.configure_ard() # Configuring SensorApp object
        
        ## Structure to store latest distance values read by sensor 1
        self.s1Data = deque([],self.numReadings)
        
        ## Structure to store latest distance values read by sensor 2
        self.s2Data = deque([],self.numReadings)
        
        # Expectation buffers for both sensors; data looks like: (int timestamp, float distance, Bool eclipsed, Bool valid, Bool sameIteration, float average, int k)
        ## Expectation buffer for sensor 1; stores distance values, timestamps, and other relevant info
        self.EBS1 = []
        
        ## Expectation buffer for sensor 2
        self.EBS2 = []
    
    # CONSTANTS
        ## Depth of environment to determine upper bound on legitimate distance readings
        self.noise = self.calibrate()
        
        ## Range of time beyond which we conclude separate people triggered sensor
        self.timeBuffer = 1200
        
        ## Range of distance beyond which we conclude separate people triggered sensor
        self.distanceBuffer = 55    
        
    def readData(self):
        """
        Reads latest distance values from SensorApp object and updates existing structures within DataFilter class with the new values.
        """
        # Read readings from sensor of the form (timestamp, distance) into an array of arrays 
        response = self.sensor.readFromSensor(self.numReadings)
        
        # updateData adds newly measured distances to sensor deques and calls other appropriate functions
        self.updateData(response)

    def sendData(self):
        """
        To be called by ServerApp. Returns existing number of people counted and resets value to 0.
        Returns:
            Number of peoplecounted
        """
        temp = self.peopleCounted
        self.peopleCounted = 0
        return temp
    
    def getData(self):
        """
        To be called by ServerApp. Returns existing number of people counted.
        
        Returns: 
            Existing local count of DataFilter object
        """
        return self.peopleCounted

    def clearData(self):
        """
        To be called by ServerApp. Resets existing number of people counted to 0.
        """
        self.peopleCounted = 0

    def calibrate(self):
        """
        Called by constructor and used to calibrate environment noise to improve the filter's ability to discern legitimate distance values read by the SensorApp object.
       
        Returns:
            Calibrated background noise with which distance readings from both sensors are compared
        """
        # Initialize minimum noise value and read times to dummy values
        minVal = 5000
        read_time = 0
        
        # Read data from sensor for 3 seconds and determine appropriate value for background noise
        while( read_time < 5000 ):
            temp = self.sensor.readFromSensor(1)
            
            # Compare distance values read from both sensors with existing minimum value: [sensor][reading_nbr][timestamp/reading]
            minVal = min([minVal,temp[0][0][1],temp[1][0][1]])
            
            # Increment time to maximum timestamp of both readings (should be sensor 2...)
            read_time = max([temp[0][0][0],temp[1][0][0]])
            
            time.sleep(0.2)
            
        # Subtract 20 to account for potential variability that was not accounted for in initial 3 seconds
        return minVal-15

    def updateData(self,response):
        """
        Work horse of the DataFilter class. Updates existing class structures with new distance values, discerns whether legitimate data has been measured, and makes judgement calls on expired distance values in either expectation buffer.
        
        Args: 
            A multidimensional array of tuples [ [ (timestamp, distance), ... , (timestamp, distance) ],[ (timestamp, distance), ... , (timestamp, distance) ] ], where each internal array corresponds to a sensor
        """

        # Temporary arrays to store legitimate distances to avoid error when pushing into expectation buffers
        temp1 = []; temp2 = []; temp3 = []
        
        # Read tuples from *2* sensors into appropriate structures
        for reading in response[0]:
            self.s1Data.append(reading)
        for reading in response[1]:
            self.s2Data.append(reading)
            
        # Determining if legitimate distance values read by sensor
        for reading in self.s1Data:
            if float(reading[1]) < self.noise:
                temp1.append(reading)
        for reading in self.s2Data:
            if float(reading[1]) < self.noise:
                temp2.append(reading)
                
        # Checking for expired expectations; if item expired, maje judgement whether or not to increment peopleCounted
        for item in self.EBS1:
            if float(self.s1Data[-1][0]) - float(item[0]) > self.timeBuffer:
                self.makeJudgementCall(item,1)
                self.EBS1.remove(item)
        for item in self.EBS2:
            if float(self.s2Data[-1][0]) - float(item[0]) > self.timeBuffer:
                self.makeJudgementCall(item,2)
                self.EBS2.remove(item)
                
        # Handle distances measured by sensor 1
        for reading in temp1:
            
            # Only look at items in expectation buffer for sensor 1 if there already exists values 
            if self.EBS1:
                for item in self.EBS1:
                    
                    # If the measured distance value is more shallow than any existing expected distances
                    if float(reading[1]) < float(item[1]) - self.distanceBuffer:
                        item[2] = True
                        
                    # Average measured distances from both sensors that fall in range
                    if abs(float(reading[1]) - float(item[5])) < self.distanceBuffer:
                        item[6] += 1
                        item[5] = float(((float(item[6])-1)/float(item[6]))*(float(item[5])+float(reading[1])/(float(item[6])-1))) 
                        itme[7] = 1
                        
            ADD = True
            for item in self.EBS2:  
                
                # If the measured distance does not have an existing expected distance in other sensor's expectation buffer
                if abs(float(reading[1]) - float(item[5])) < self.distanceBuffer:
                    ADD = False
                    item[3] = True
                    item[6] += 1
                    item[5] = float(((float(item[6])-1)/float(item[6]))*(float(item[5])+float(reading[1])/(float(item[6])-1)))    
                    item[7] = 1
                    
            for item in self.EBS1:
                
                # If the measured distance corresponds to previously measured distance within certain timeframe
                if abs(float(reading[0]) - float(item[0])) < self.timeBuffer:
                    ADD = False            
            if ADD:
                self.EBS2.append([reading[0],reading[1],False,False,True,reading[1],1])
                
        # Handle distances measured by sensor 2
        for reading in temp2:
            
            if self.EBS2:
                for item in self.EBS2:
                    
                    # If the measured distance value is more shallow than any existing expected distances
                    if float(reading[1]) < float(item[5]) - self.distanceBuffer:
                        item[2] = True
                        
                    # Average measured distances from both sensors that fall in range
                    if abs(float(reading[1]) - float(item[5])) < self.distanceBuffer:
                        item[6] += 1
                        item[5] = float(((float(item[6])-1)/float(item[6]))*(float(item[5])+float(reading[1])/(float(item[6])-1)))   
                        item[7] = 2
                        
            ADD = True          
            for item in self.EBS1:
                
                # If the measured distance does not have an existing expected distance in other sensor's expectation buffer
                if abs(float(reading[1]) - float(item[5])) < self.distanceBuffer:
                    ADD = False
                    item[3] = True
                    item[6] += 1
                    item[5] = float(((float(item[6])-1)/float(item[6]))*(float(item[5])+float(reading[1])/(float(item[6])-1))) 
                    item[7] = 2
                    
            for item in self.EBS2:
                # If the measured distance corresponds to previously measured distance within certain timeframe
                if abs(float(reading[0]) - float(item[0])) < self.timeBuffer:
                    ADD = False                     
            if ADD:
                self.EBS1.append([reading[0],reading[1],False,False,False,reading[1],1])
                
        # Fixing new value truth
        for item in self.EBS2:
            item[4] = False        

    def makeJudgementCall(self, item, sensor):
        """
        Ultimately determines whether a distance value expired in either expectation buffer should be counted as a person walking in a particular direction.
        
        Args:
            item: an element of the expectation buffer
            sensor: is the number of the sensor (in this case we only support 2 sensors)
        """
        
        # If valid and ((expectation not for sensor 1 and last value not sensor 1) or eclipsed)
        if item[3] and (not (sensor == 1 and item[7] == 1) or item[2]):
            self.peopleCounted += 1