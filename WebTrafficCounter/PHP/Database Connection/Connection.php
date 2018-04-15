<?php


/**
 * @class Connection
 *
 * @brief A connection to the database. An object of this class can open/close a connection to the database, get the status of the connection, and perform a query.
 *
 */

class Connection
{
    var $conn; //!< Represents the connection to the database.

    var $db; //!< Represents the database.
    var $databaseName; //!< Name of the database.
    var $username; //!< User name to login to the database.
    var $password; //!< Password to login to the database.

    /**
     * Connection constructor.
     * @brief Initializes a Connection object. Opens a connection to the database and sets values for member variables.
     */
    public function __construct() {
        $this->db = "database.cse.tamu.edu";
        $this->databaseName = "meratexas123";
        $this->username = "meratexas123";
        $this->password = "111111aA";
        $this->conn = $this->OpenConnection();
    }

    /**
     * @brief Establishes a connection to the databases.
     * @return PDO PHP Data Object to allow interaction with the database.
     */
    public function OpenConnection()// connect to MySQL DB Server
    {
        try
        {
            //connect to database through PDO
            return new PDO('mysql:host='.$this->db.';dbname='.$this->databaseName, $this->username, $this->password);
        }
        // Handle a connection exception
        catch (PDOException $e) {
            print "Error: " . $e->getMessage() . "<br/>";
            die();
        }
    }

    /**
     * @brief Returns a connection to the database.
     * @return PDO the connection to the database
     */
    public function GetConnection() {
        return $this->conn;
    }

    /**
     * @brief Closes the connection to the database.
     *
     */
    public function CloseConnection() {
        $this->conn = null;
    }

    /**
     * @brief Executes an sql query string.
     * @param $sqlQuery string with  an sql syntax query.
     * @return array
     */
    public function executeQuery($sqlQuery) {
        // Execute the query or have the process ide
        $rs = $this->conn->query($sqlQuery) or die("Could not execute query '$sqlQuery' "); //result of the query

        // Return the result of the query
        return $rs->fetchAll(PDO::FETCH_NUM);
    }

}

