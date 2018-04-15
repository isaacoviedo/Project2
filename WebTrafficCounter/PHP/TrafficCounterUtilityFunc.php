<?php

include "Database Connection/DatabaseManager.php";



// Calculate the mean
function CalculateMean($array){
    
    $count = count($array);
    
    // Don't calculate unless the array is nonzero 
    if(!is_array($array) || $count ==0){

        return -1;

    } else{

        $sum = array_sum($array);

        $mean = $sum / $count;

        // Check that there wasn't an error
        if($mean != null) {
        
            return $mean;
        
        }else{
        
            return -1;
        
        }
    }
}


 // Calculate the median 
function CalculateMedian($array) {

    $count = count($array);
    
    // Don't bother if the array is empty
    if(!is_array($array) || $count == 0){
    
        return -1;
    
    } else{
        
        rsort($array);
        
        $middle = round(count($array) / 2);
        
        $median = $array[$middle-1];

        // Make sure not to return NULL
        if($median != null) {
        
            return $median;
        
        }else{
           
            return false;
        
        }
    }
}


// Helper function to deal with TimeStamp Conversion
function GetTimeStampAndCountBetweenDates($startDateTime, $endDateTime) {


    // Create and connect tot he datbase manager
    $databaseConnection = new DatabaseManager();
    
    $databaseConnection->Connect();

    // Convert the timestamps to time objects
    $startEpochDateTime = strtotime($startDateTime);

    $endEpochDateTime = strtotime($endDateTime);


    // Make sure start is not false
    if ($startEpochDateTime === false) {
        echo 'failed to convert date to epoch format';
        exit;
    }

    // Make sure end is not false
    if ($endEpochDateTime === false) {
        echo 'failed to convert date to epoch format';
        exit;
    }

    // Build the timestamp Query
    $timeStampAndCountQuery = "SELECT Time_Stamp, Count FROM People_Count_Data_Dev WHERE Time_Stamp >= '$startEpochDateTime' && Time_Stamp <= '$endEpochDateTime'";
    
    // Perform the timestamp query
    $assoc_array = $databaseConnection->PerformQuery($timeStampAndCountQuery);

    // Validate that we got input back. If not return an empty array
    if (empty($assoc_array)) {
        //echo "Could not successfully run query ($timeStampAndCountQuery) from Database";
        echo "No data available for the provided dates<br>";
        return array();
    }

    // Return result
    return $assoc_array;
}

?>
