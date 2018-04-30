<?php

include("Connection.php");

/**
 * @class DatabaseManager
 *
 * @brief Manages a connection to the database. This class provides functions to manage database connection.
 */
class DatabaseManager
{
    var $databaseConnection; //!< A connection to the database that is managed by this class.
    var $connectedToDatabase = false; //!< Status of the connection to the database.

    /**
     * DatabaseManager constructor.
     * @brief Initializes an object od DatabaseManager Class.
     */
    public function __construct()
    {
        $this->databaseConnection = new Connection();
        $this->connectedToDatabase = false;
    }

    /**
     * @brief Establishes a connection to the database.
     */
    public function Connect()
    {
        $this->connectedToDatabase = true;
    }

    /**
     * @brief Return the database connection's status
     * @return bool status of the connection to the database.
     */
    public function GetConnectionStatus() {
        return $this->connectedToDatabase;
    }


    /**
     * @brief Disconnects the database.
     */
    public function Disconnect()
    {
        $this->connectedToDatabase = false;
        $this->databaseConnection->CloseConnection();
    }

    /**
     * @brief Executes a query if database is connected.
     * @param $sqlQuery string
     * @return $result array of entries from database.
     */
    function PerformQuery($sqlQuery)
    {
        // Do not perform a query if we are not connecteds
        if ($this->connectedToDatabase == false) {
            echo("$sqlQuery <br> \n");
            die();
        }

        // Perform the query
        $result = $this->databaseConnection->executeQuery($sqlQuery);

        // Return the result
        return $result;
    }

}