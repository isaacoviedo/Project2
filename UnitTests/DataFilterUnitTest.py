"""@package DataFilter_UnitTest
Read .csv file with timestamps and corresponding distance values and feed through the data filter to determine accuracy, debug, and improve logic. 
"""

class UnitTest:
    
    """Instantiate a DataFilter object."""
    def __init__(self):
        
        from DataFilterTest import DataFilter
        self.Filter = DataFilter()   
    
    """Read a .csv file and pass data to the DataFilter object, then print the filter's determined count."""
    def Run_Test(self, fileName):
        
        import time
        start = time.time()
        
        import csv
        
        # Read data from text file into two columns
        with open(fileName) as filterTest:
            testFile = csv.reader(filterTest, delimiter=',')
            for line in testFile:
                  
                self.Filter.readData([[(line[0],line[1])],[(line[2],line[3])]])
    
        end = time.time()
        
        # Statistics for the test
        print("Time taken to run the test:: ", (end - start), '\n')
        print("Count value:: ", self.Filter.peopleCounted, '\n')
        
"""Instantiate a UnitTest object and perform the test with the appropriate .csv file, 'filter_test.csv.'"""
def main():
    
    test = UnitTest()
    
    test.Run_Test("filter_test.csv")
    
main()