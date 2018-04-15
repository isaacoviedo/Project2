<style>
    <?php include '../CSS/main.css'; ?>
</style>

<div class="ChartArea" id="ChartArea"> </div>

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
            Select start and end date to analyze REC usage.
        </p>
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
                $arrayOfCountValuesBetweenUserInputDates = GetTimeStampAndCountBetweenDates($_POST['StartDateInput'], $_POST['EndDateInput']);

                // Ensure that dates selected by the user had some data
                if(!empty($arrayOfCountValuesBetweenUserInputDates)) {

                    // get an array of the number of students
                    $numberOfStudents = count(array_column($arrayOfCountValuesBetweenUserInputDates, 1));

                    // calculate mean and median
                    $mean = CalculateMean(array_column($arrayOfCountValuesBetweenUserInputDates, 1));
                    $median = CalculateMedian(array_column($arrayOfCountValuesBetweenUserInputDates, 1));

                    //display values to the user.
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
        if( !empty($_POST) && isset($_POST['UsageDateInput']) ) {
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
                if( !empty($arrayOneDayFromUserInput) && !empty($arrayOneWeekFromUserInput) ) {

                    // get time stamp and count arrays for one day and one week
                    $countArrayForOneDay = array_column($arrayOneDayFromUserInput, 1);
                    $timeStampArrayForOneDay = array_column($arrayOneDayFromUserInput, 0);
                    $countArrayForOneWeek = array_column($arrayOneWeekFromUserInput, 1);
                    $timeStampArrayForOneWeek = array_column($arrayOneWeekFromUserInput, 0);

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
                    echo "For the day";
                    echo "<br>";
                    echo "Lowest Point recorded at time: $lowestPointTimeDay";
                    echo "<br>";
                    echo "Highest Point recorded at time: $highestPointTimeDay";
                    echo "<br>";
                    echo "For the next week";
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