<?php

/**
 * @class ValidationTests
 *
 * @brief Provides validation code for user inputs. This class provides member functions to validate integer and date inputs.
 */

class ValidationTests extends PHPUnit_Framework_TestCase
{

    /**
     * @brief Returns the input date if its valid and false otherwise.
     * @return bool|string
     */
    public function DateValidation()
    { //Copy paste of validation code
        //The user can only enter start date time and end date time.
        //Arduino can dump count(integer) too
        //Rest of the input is checkboxes and radio buttons and thus need not be validated
        //Only need to validate dates and integers

        //check if we have data in post array
        if (isset($_POST['startDateInput']) && isset($_POST['endDateInput'])
            && !empty($_POST['startDateInput'] && !empty($_POST['endDateInput']))) {

            $startDateInput = trim($_POST['startDateInput']);
            $endDateInput = trim($_POST['endDateInput']);
        }

        //set syntax for date time format in regex
        $regex = '/^((([1-2][0-9])|([1-9]))/([2])/[0-9]{4})|((([1-2][0-9])|([1-9])|(3[0-1]))/((1[0-2])|([3-9])|([1]))/[0-9]{4})$/';

        if (preg_match($regex, $startDateInput) && preg_match($regex, $endDateInput)) {
            $validated_start_date = $startDateInput;
            $validated_end_date = $endDateInput;

            //Update the time stamps in database in db
            $error = '';
            return true;
        }
        else {
            $error = 'Invalid date format<br />';

        }

        return $error;
    }

    /**
     * @brief Returns null string if integer input is valid and an error otherwise.
     * @return string
     */
    public function IntegerValidation()
    { //Copy paste of validation code
        //The user can only enter start date time and end date time.
        //Arduino can dump count(integer) too. The database stores time stamps as int. Example: 20180612 is 12 Jun 2018
        //Rest of the input is checkboxes and radio buttons and thus need not be validated
        //Only need to validate dates and integers

        // validate an integer input
        if (filter_var($_POST['numOfPeople'], FILTER_VALIDATE_INT) !== false) {
            $error = '';
            return $error;
        }

        $error = 'Invalid date format<br />';
        return $error;

    }
}

?>