<style>
    <?php include '../CSS/main.css'; ?>
</style>

<div class="Chart1Area" id="Chart2Area"> </div>
<div class="Chart2Area" id="Chart2Area"> </div>

<?php
include 'TrafficCounterUtilityFunc.php';
?>

<div class="ChartOptionsArea">
    <p>Choose the start and end date to display chart.</p>

    <form id="chartOptions" action="index.php" method="post">
        <label>
            Start Date:<input type="datetime-local" id="GraphStartDate" name="StartDateInputGraph">
        </label>
        <label>
            End Date:<input type="datetime-local" id="GraphEndDate" name="EndDateInputGraph">
        </label>
        <br>
        <br>
        <label>
            <button onclick="DisplayChartOnButtonClick();return false;" style="display: block; margin: 0 auto;">Graph</button>
        </label>
        <p>
            Select lot number, start and end date to analyze parking usage.
        </p>
        <label>
            Lot:<select name="lot" id="lot">
                    <option value="lot54">Lot 54</option>
                    <option value="lot35">Lot 35</option>
                </select>
        </label>
        <label>
            Start Date:<input type="datetime-local" id="StatisticsStartDate" name="StartDateInput">
        </label>
        <br>
        <label>
            End Date:<input type="datetime-local" id="StatisticsEndDate" name="EndDateInput">
        </label>
        <br>
        <?php

        // Check that post data is not empty and user has set the start and end dates to see statistics
        if( !empty($_POST) && isset($_POST['StartDateInput']) && isset($_POST['EndDateInput']) ) {

            // another check to ensure that post values are not null.
            if ($_POST['StartDateInput'] != null && $_POST['EndDateInput'] != null) {

                // store start and end dates in variables
                $userStartDate = $_POST['StartDateInput'];
                $userEndDate = $_POST['EndDateInput'];

                // output start and end date to the user
                echo "<output>Start Date: $userStartDate</output>";
                echo " ";
                echo "<output>End Date: $userEndDate</output>";
                echo "\n";

                // GEt an array with two columns. First column has entries of time stamps. Second column has entries of the number of people.
                $arrayOfCountValuesBetweenUserInputDates = GetTimeStampAndCountBetweenDates($userStartDate, $userEndDate);

                // Ensure that dates selected by the user had some data
                if(!empty($arrayOfCountValuesBetweenUserInputDates)) {
                    $countArray = array();
                    foreach($arrayOfCountValuesBetweenUserInputDates as $element) {
                        array_push($countArray, $element[1]);
                    }

                    $numberOfStudents = array_sum($countArray);
                    $mean = CalculateMean($countArray);
                    $median = CalculateMedian($countArray);

                    echo "<br>";
                    echo "Number of students: $numberOfStudents";
                    echo "<br>";
                    echo "Average Number of students: $mean";
                    echo "<br>";
                    echo "Median: $median";
                }
            }
        }
        ?>
        <br>

        <p>
            Enter a date to get the highest and lowest number of students
            <br>
            for that day and week.
        </p>
        <label>
            Date:<input type="date" id="UsageDate" name="UsageDateInput">
        </label>
        <br>

        <?php
        // Ensure that the required values are set and not null
        if(!empty($_POST) && isset($_POST['UsageDateInput'])) {
            if ( $_POST['UsageDateInput'] != null ) {

                // initialize a variable that denotes the date. Highest and lowest point will be displayed to the user based on the duration of
                // 1 week and 24 hours from this date.
                $UserAnalysisDate = $_POST['UsageDateInput'];
                $targetDayEndDate = date('Y-m-d H:i:s', strtotime($UserAnalysisDate . ' +1 day'));
                $targetWeekEndDate = date('Y-m-d H:i:s', strtotime($UserAnalysisDate . ' +7 day'));

                // output the date to user
                echo "<output>Analysis of Date: $UserAnalysisDate</output>";
                echo "\n";

                // get arrays(with columns of time stamps and number of people) for the next day and the next week
                $arrayOneDayFromUserInput = GetTimeStampAndCountBetweenDates($UserAnalysisDate, $targetDayEndDate);
                $arrayOneWeekFromUserInput = GetTimeStampAndCountBetweenDates($UserAnalysisDate, $targetWeekEndDate);

                // Both arrays will not be empty if there is data to be analyzed
                if(!empty($arrayOneDayFromUserInput) && !empty($arrayOneWeekFromUserInput)) {

                    // get time stamp and count arrays for one day and one week
                    $countArrayForOneDay = array();
                    foreach($arrayOneDayFromUserInput as $element) {
                        array_push($countArrayForOneDay, $element[1]);
                    }
                    $timeStampArrayForOneDay = array();
                    foreach($arrayOneDayFromUserInput as $element) {
                        array_push($timeStampArrayForOneDay, $element[0]);
                    }
                    $countArrayForOneWeek = array();
                    foreach($arrayOneWeekFromUserInput as $element) {
                        array_push($countArrayForOneWeek, $element[1]);
                    }
                    $timeStampArrayForOneWeek = array();
                    foreach($arrayOneWeekFromUserInput as $element) {
                        array_push($timeStampArrayForOneWeek, $element[0]);
                    }

                    //find the indices that has lowest and highest count and store them
                    $lowestPointTimeDayIndex = array_keys($countArrayForOneDay, min($countArrayForOneDay))[0]; //find index of the lowest element
                    $highestPointTimeDayIndex = array_keys($countArrayForOneDay, max($countArrayForOneDay))[0];
                    $lowestPointTimeWeekIndex = array_keys($countArrayForOneWeek, min($countArrayForOneWeek))[0]; //find index of the lowest element
                    $highestPointTimeWeekIndex = array_keys($countArrayForOneWeek, max($countArrayForOneWeek))[0];

                    // find the corresponding time stamps at those indices
                    $lowestPointTimeDay = date('Y-m-d H:i:s', $timeStampArrayForOneDay[$lowestPointTimeDayIndex]);
                    $highestPointTimeDay = date('Y-m-d H:i:s', $timeStampArrayForOneDay[$highestPointTimeDayIndex]);
                    $lowestPointTimeWeek = date('Y-m-d H:i:s', $timeStampArrayForOneWeek[$lowestPointTimeWeekIndex]);
                    $highestPointTimeWeek = date('Y-m-d H:i:s', $timeStampArrayForOneWeek[$highestPointTimeWeekIndex]);

                    // display calculation to user
                    echo "<br>";
                    echo "For the day:";
                    echo "<br>";
                    echo "Lowest Point recorded at time: $lowestPointTimeDay";
                    echo "<br>";
                    echo "Highest Point recorded at time: $highestPointTimeDay";
                    echo "<br>";
                    echo "For the next week:";
                    echo "<br>";
                    echo "Lowest Point recorded in this week: $lowestPointTimeWeek";
                    echo "<br>";
                    echo "Highest Point recorded in this week: $highestPointTimeWeek";
                }
            }
        }
        ?>
        <br>
        <label>
            <!--<button style="display: block; margin: 0 auto;">Calculate</button>-->
            <input type="submit" value="submit"/>
        </label>
    </form>
</div>