'''
Title  :: Data Filter
Author :: William Ogletree
Brief  :: The filter accepts distance values read by the sensor from the server application and processes the data to determine 
              the number of pedestrians walking in a prior-specified direction within a given time frame.
*Sonar sensors need to be placed in appropriate position PRIOR to instantiating the DataFilter class (see calibrate())*
'''

"""@package DataFilter
The rationale behind the implementation is that if an individual walks through a sensor, we expect to read a similar distance value in the other sensor within a relatively 
small timeframe. We use 'expectation buffers' to keep track of our expectations. If we do not read a distance value we expect within a given timeframe, then we know something 
is awry. We do not have all the information, so we need to make judgement calls based on what we do know. We keep track of various occurrences while a value exists in either 
expectation buffer to better help us make reasonable judgements to discern the direction and validity of measured data.
"""

# IMPORTS
from sensorApp import SensorApp
from collections import deque
import time

class DataFilter:
    """DataFilter instantiates SensorApp and processes distance values to determine the number of people walking in one direction when traffic is potentially bidirectional. 
    The DataFilter class itself is instantiated within the ServerApp class. """
    
    def __init__(self):
        """Instantiates SensorApp object and sets constants as specified. Calibrates environment noise."""
    # VALUES
        self.peopleCounted = 0
        #self.variability = 0

        # How many readings do we want from sensor each cycle
        self.numReadings = 1

    # STRUCTURES
        # Initializing Sensor class
        self.sensor = SensorApp( "COM1",250000,5,[2,5],[9,12] )
        self.sensor.configure_ard()
        # Structures to store reading values
        self.s1Data = deque()
        self.s2Data = deque()
        # Expectation buffers for both sensors; data looks like:
        #                        (int timestamp, bool valid, float average_dist, int count)
        #                        Each element of the buffers represents a possible person entering
        #                        timestamp = time of entrance
        #                        valid = is this a valid reading?
        #                        average_dist = average distance of the person from the sensor in question
        #                        count = number of sensor readings for this particular person
        self.EBS1 = []
        self.EBS2 = []
    
    # CONSTANTS
        # Look at background noise from sensor and establish depth of environment
        #self.noise = 400
        self.noise = self.calibrate()
        # Range of distances/times where we conclude same person
        self.timeBuffer = 1200
        self.distanceBuffer = 55  
        
    def renewPersonata(self):
        """Reads latest distance values from SensorApp object and updates existing structures within DataFilter class with the new values."""
        # Read readings from sensor of the form (timestamp, distance) into an array of arrays 
        #    ("Reading Data")
        response = self.sensor.readFromSensor()
        # updateData newPersons newly measured distances to sensor deques and calls other appropriate functions
        self.updateData(response)

    def sendData(self):
        """To be called by ServerApp. Returns existing number of people counted and resets value to 0."""
        temp = self.peopleCounted
        self.peopleCounted = 0
        return temp
    
    def getData(self):
        """To be called by ServerApp. Returns existing number of people counted."""
        return self.peopleCounted

    def clearData(self):
        """To be called by ServerApp. Resets existing number of people counted to 0."""
        self.peopleCounted = 0

    def calibrate(self):
        """Called by constructor and used to calibrate environment noise to improve the filter's ability to discern legitimate distance values read by the SensorApp object."""
        minVal = 5000
        read_time = 0

        # Read data from sensor for 3 seconds and determine appropriate value for background noise
        while( read_time < 3000 ):
            temp = self.sensor.readFromSensor(1)
           # print(str(temp))
            # Compare distance values read from both sensors with existing minimum value
            # [sensor][reading_nbr][timestamp/reading]
            minVal = min([minVal,temp[0][0][1],temp[1][0][1]])
            # Increment time to maximum timestamp of both readings (should be sensor 2...)
            read_time = max([temp[0][0][0],temp[1][0][0]])
            time.sleep(0.2)

        # Subtract 15 to account for potential variability that was not accounted for in initial 3 seconds
        return minVal-15

    def updateData(self,response):
        """Work horse of the DataFilter class. Updates existing class structures with new distance values, discerns whether legitimate data has been measured, 
        and makes judgement calls on expired distance values in either expectation buffer."""
        # Temporary arrays to store legitimate distances to avoid error when pushing into expectation buffers
        validData1 = []; validData2 = []
        self.s1Data.clear()
        self.s2Data.clear()

        # Read tuples from *2* sensors into appropriate structures
        for reading in response[0]:
            self.s1Data.append(reading)
        for reading in response[1]:
            self.s2Data.append(reading)

        # Determining if legitimate distance values read by sensor
        for reading in self.s1Data:
            if float(reading[1]) < self.noise:
                validData1.append(reading)
                print("distance = " + str(reading[1]))
        for reading in self.s2Data:
            if float(reading[1]) < self.noise:
                validData2.append(reading)
                print("distance = " + str(reading[1]))

        # Checking for expired expectations
        for item in self.EBS2:
            if float(self.s2Data[-1][0]) - float(item['timestamp']) > self.timeBuffer:
                self.makeJudgementCall(item,2)
                self.EBS2.remove(item)


        # Handle distances measured by sensor 1
        for reading in validData1:
            newPerson = True
            if self.EBS1:
                for item in self.EBS1:
                    # Average measured distances from both sensors that fall in range
                    if abs(float(reading[1]) - float(item['average_dist'])) < self.distanceBuffer:
                        newPerson = False
                        item['count'] += 1
                        item['average_dist'] = float(item['average_dist']*(item['count']-1) + reading[1])/item['count']
                 
            # There is probably a new person passing the sensors. Create another buffer for them.       
            if newPerson:
                self.EBS1.append(dict(timestamp=reading[0],valid=False,average_dist=reading[1],count=1))
                self.EBS2.append(dict(timestamp=reading[0],valid=False,average_dist=reading[1],count=0))

        # Handle distances measured by sensor 2
        for reading in validData2:
            if self.EBS2:
                for item in self.EBS2:
                    # Average measured distances from both sensors that fall in range
                    if abs(float(reading[1]) - float(item['average_dist'])) < self.distanceBuffer:
                        item['valid'] = True
                        item['count'] += 1
                        item['average_dist'] = float(item['average_dist']*(item['count']-1) + reading[1])/item['count']  

    def makeJudgementCall(self, item, sensor):
        """Ultimately determines whether a distance value expired in either expectation buffer should be counted as a person walking in a particular direction."""
        # Logic can be found in other documentation
        if item['valid']:
            self.peopleCounted += 1
            print(self.peopleCounted)



if (__name__ == "__main__"):
    filter = DataFilter()
    while(1):
        filter.renewPersonata()
        time.sleep(0.15)