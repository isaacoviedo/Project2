<?php

include("DatabaseManager.php");

/**
 * @file UpdateDatabas.php
 * @brief Provides code to allow a user with admin privilege to update or insert values in the database.
 */
$databaseManager = new DatabaseManager();

// Time stamp for the entry
$time_stamp = $_POST["time"];

// Count from the sensor
$count = $_POST["count"];

// Validate the time stampe
$errorTimeInput = ValidateInputToDatabase($time_stamp);

// Validate the count coming into the system
$errorCount = ValidateInputToDatabase($count);


// Execute query when both are valid
if($errorTimeInput == null && $errorCount == null) {

    $query = "INSERT INTO People_Count_Data_Web_Server_Dev (Time_Stamp, Count) VALUES ('".$time_stamp."','".$count."')";

    // Connect to the database
    $databaseManager->Connect();

    // Perform the Query
    $databaseManager->PerformQuery($query);

    // Disconnect from the database
    $databaseManager->Disconnect();

}

/**
 * @brief Returns null if there's a valid input and an error otherwise.
 * @param $numOfPeople int
 * @return null|string
 */
function ValidateInputToDatabase($numOfPeople) {

    // Check if the numOfPeople is an integer. If it is return null, and keep on partying
    if(filter_var($numOfPeople, FILTER_VALIDATE_INT) !== false){

        $error = null;
        
        return $error;
    }
    // Return the error
    $error = 'Invalid date format<br />';
    return $error;
}

?>