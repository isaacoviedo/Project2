<?php
include("TrafficCounterUtilityFunc.php");

// This script processes an AJAX request to send data that is graphed on client side
if(isset($_POST['GraphStartDate']) && isset($_POST['GraphEndDate'])) {
    $post_result = array(); // declare associative array with Time stamp as keys and count as value

    // Retrieve the start and end date from AJAX request
    $phpFormatStartDate = $_POST['GraphStartDate'];
    $phpFormatEndDate = $_POST['GraphEndDate'];

    // Get columns (timestamp and count) values between start and end dates provided by the AJAX request
    $database_result = GetTimeStampAndCountBetweenDates($phpFormatStartDate, $phpFormatEndDate);

    // Get an array of Time stamps and another array of number of people in the last 15 minutes
    $TimeStamp_result = array_column($database_result, 0);
    $Count_result = array_column($database_result, 1);

    // make a JSON style object with Time stamps as keys and number of people aka Count as value
    for($i = 0; $i < Count($TimeStamp_result); $i++) {
        $post_result[ (string)date("Y-m-d H:i:s", (string)$TimeStamp_result[$i]) ] = $Count_result[$i];
    }

    // tells the server to return JSON type result and not html
    header('Content-Type: application/json');

    //encode the array to a json object
    echo json_encode($post_result);
    die();
}

?>