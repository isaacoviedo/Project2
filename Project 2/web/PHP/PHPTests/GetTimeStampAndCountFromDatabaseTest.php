<?php

include "../TrafficCounterUtilityFunc.php";

/**
 * @class GetTimeStampAndCountFromDatabaseTest
 *
 * @brief Tests Getting values from the database. The data is returned by the database in the form of an array with two columns.
 */
class GetTimeStampAndCountFromDatabaseTest extends \PHPUnit\Framework\TestCase
{
    var $dbManager; //!< Test connection to test getting values from database.

    /**
     * GetTimeStampAndCountFromDatabaseTest constructor.
     * @brief Initializes variables needed for further tests.
     */
    public function __construct()
    {
        // Initialize a DatabaseManager object for subsequent tests.
        $this->dbManager = new DatabaseManager();
        $this->dbManager->Connect();
    }

    /**
     * @brief Asserts that the number of time stamps and count values are the same.
     *
     */
    public function testValuesReceived() {
        // Test that values are received from the database.

        //declare start and end date
        $testStartDate = '3/12/2017';
        $testEndDate = '3/12/2030';

        //Get two columns in an an array with first column with Time stamps and second column with number of people.
        $testResult = GetTimeStampAndCountBetweenDates($testStartDate, $testEndDate);

        //Get first and second column
        $timeStampArray = array_column($testResult, 0);
        $countArray = array_column($testResult, 1);

        //Assert that the same number of time stamps and count entries are returned
        $this->assertEquals(count($timeStampArray), count($countArray));
    }
}

?>