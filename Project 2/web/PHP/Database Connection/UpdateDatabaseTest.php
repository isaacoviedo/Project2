<?php

include("DatabaseManager.php");

/**
 * @class UpdateDatabaseTest
 *
 * @brief Tests member methods of DatabaseManager class.
 */
class UpdateDatabaseTest extends \PHPUnit\Framework\TestCase
{
    var $dbManager; //!< Test connection to test functions of DatabaseManager class.

    /**
     * UpdateDatabaseTest constructor.
     * @brief Initializes values for tests on database interaction.
     */
    public function __construct()
    {
        $this->dbManager = new DatabaseManager();
    }

    /**
     * @brief Tests if a connection can be opened properly.
     */
    public function testOpenConnection() {

        $this->assertSame($this->dbManager->GetConnectionStatus(), false); // initially disconnected

        // Connect
        $this->dbManager->Connect();

        $this->assertSame($this->dbManager->GetConnectionStatus(), true); // connected to database
    }


    /**
     * @brief Tests if the correct values are added to the database.
     */
    public function testCorrectValuesAddedToDatabase() {
        $this->dbManager->Connect();

        // Build Query
        $sql_query_select = "SELECT * FROM People_Count_Data_Web_Server_Dev WHERE Time_Stamp = '201812061205'";

        // Verify Result
        $verifyResult = $this->dbManager->PerformQuery($sql_query_select);

        // Check if it's valid
        $this->assertSame($verifyResult['Count'], '1574893'); //same data was updated
        
        // Connect to the database
        $this->dbManager->Connect();
    }

    /**
     * @brief Tests that database connection is closed properly.
     * @dataProvider testOpenConnection
     */
    public function testCloseConnection() {

        // Connect to the database
        $this->dbManager->Connect();

        $this->assertSame($this->dbManager->GetConnectionStatus(), true); // initially connected

        // Disconnect from the datbase
        $this->dbManager->Disconnect();

        $this->assertSame($this->dbManager->GetConnectionStatus(), false); // disconnected after calling Disconnect

    }


















}
