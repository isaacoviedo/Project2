<?php

	if(isset($_POST['predictDay'])) {
	    $post_result = array(); // declare associative array with Time stamp as keys and count as value

	    // Retrieve the start and end date from AJAX request
	    $predictDay = $_POST['predictDay'];
	    $beginDate = dayToDate($predictDay);

	    // averages traffic data for this day across past four weeks
	    for($weeksAgo=0;$weeksAgo<5;$weeksAgo++) {
	    	$dayTimestamp = strtotime($beginDate . " -" . $weeksAgo . " weeks");

	    	// gets traffic data for each hour in the day
	    	for($hour=0;$hour<24;$hour++) {
	    		$hourTimestamp = $dayTimestamp + $hour*3600;
	    		$nextHourTimestamp = $hourTimestamp + 3600;
	    		$hourString = date("Y-m-d H:i:s", $hourTimestamp);
	    		$nextHourString = date("Y-m-d H:i:s", $nextHourTimestamp);

	    		$trafficData = GetTimeStampAndCountBetweenDates($hourString, $nextHourString);
	    		$count = $trafficData[0];

	    		if($post_result[(string)date("H", $hourTimestamp)])
	    			$post_result[(string)date("H", $hourTimestamp)] = ($post_result[(string)date("H", $hourTimestamp)] + $count)/2;
	    		else
	    			$post_result[(string)date("H", $hourTimestamp)] = $count;
	    	}
	    }

	    // tells the server to return JSON type result and not html
	    header('Content-Type: application/json');

	    //encode the array to a json object
	    echo json_encode($post_result);
	    die();
	}


	function dayToDate($dayName) {
		$timestamp = strtotime($dayName . " this week");
		$date = date("d", $timestamp);
		return $date;
	}

?>