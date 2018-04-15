/*
  Becuase we are basically doing the same call/response with Firmata we
  might as well build our own custom version... with a few new tricks

  Example Connection Protocol::
  CON5,TRI,1,2,3,4,ECH,5,6,7,8,\n 

  Main Communication protocol::
    - Three Characters for Command
    - Followed by actual data being sent back and forth
    - End of command/data flow is delineated by an endline character
  Supported commands
  - RDY = Ready to be configured
  - CON = Connected, about to send data
          Followed by updateRate, TRI, triggerPins,ECH, echoPins, EL
  - SUC = Succesfully Configured
  - REQ = Request for data,
          Followed by EL
  - REP = Response to request for data
          Followed by the local buffer of last read values
  - PRT = Debugging data to be printed,
          Followed by some integers/Characters
*/

#include <String.h>

#define HCSRO4_CONSTANT 0.017

// Instantiate variables to dummy values
unsigned long loop_time_millis = 0; //!< Time for the Update Loop to complete
int number_trig_pins = -1; //!< number of trigger pins that have been configured, should be the same number as echo_pins
int number_echo_pins = -1; //!< number of echo pins that have been configured, should be the same number as trig_pins
int trigPins[]= {-1,-1,-1,-1}; //!< trigger pin values
int echoPins[] = {-1,-1,-1,-1}; //!< echo pin values

// Instantiate the following with preliminary values
long runTime = 0; //!< the amount of time that the function is taking to loop through
int state = 0; //!< State of the Configuration header state machine, this is only global because Arduino has some funky scope magic that requires this
int startTime = millis(); //!< initial start time of the application. Utilized to find the timestamps stored with the readings
int update_rate = 5; //!< The update rate in Hz that the sensors are running at. Directly related to loop_time_millis
bool isConfigured = false; //!< Flipped when the sensor is configured. Initiates readings in the loop() function
int nbr_readings = 10; //!< Maximum number of redadings to take per Request Command
String command_str = "";//!< Master command string that acts as our buffer to the commands coming in on the serial connection
unsigned long time; //!< Used for QA and runtime assurance testing... Sort of an artifact. We call him Jeff. Jeff can stay. 

// Both of these are treated as FILO Queues
double readDistances[4][10]; //!< FILO Queues for the readings
unsigned long readTimes[4][10]; //!< FILO Queues for the times

/* Forward Declarations **/
/*! \fn void resetConfigurationToDefault(void) 
  \brief Reset existing variables to dummy values

*/
void resetConfigurationToDefault(void);

/*! \fn int readConfiguration(void)
  \brief Read necessary data from Arduino to properly configure pins and serial ports

  \return 0 if failure, 1 if success
*/
int readConfiguration(void);

/*! \fn int findConfHeader(void)
  \brief Read through characters until we have found the CON sequence

  \return 1 if configuration header found, 0 if not
*/
int findConfHeader(void);

/*! \fn void readCommand(void)
 \brief More commands can be addded here, but we only support the sending and receiving of REP commands right now
 
*/
void readCommand(void);

/*! \fn void updateReadingsData(double newReadings[], unsigned long newTimes[])
 \brief Updating existing data structures holding distance values read from sensors

*/
void updateReadingsData(double newReadings[], unsigned long newTimes[]);



/*! \fn void setup();
 \brief Setup a 250 kHz connection to the host computer

*/
void setup();


/*! \fn void loop();
 \brief The primary function that continually reads from pins and updates existing data structures with new distance values
*/
void loop();



// ######### IMPLEMENTATION AFTER THIS POINT ##########

 
void updateReadingsData(double newReadings[], unsigned long newTimes[]){
  // Move in the new data and remove the old ones
  for(int i=0; i < 4; i++){
    for (int j=9;j>=0; j--){
      if (j == 0){
        readTimes[i][j] = newTimes[i];
        readDistances[i][j] = newReadings[i];
      }else {
        readTimes[i][j] = readTimes[i][j-1];
        readDistances[i][j] = readDistances[i][j-1];
      }
    }
  }
}


void resetConfigurationToDefault(void){
  number_echo_pins = -1;
  number_trig_pins = -1;
  update_rate = 5;

  // Set each trigger pin, echo pin, distance values, and timestamp to dummy values
  for (int i =0 ; i < 4; i++){
    trigPins[i] = -1;
    echoPins[i] = -1;
    for (int j=0; j < 10; j++){
        readDistances[i][j] = -1.0;
        readTimes[i][j] = 0;
    }
  }
}


int readConfiguration(void){
  if (findConfHeader()){
    // Now we parse the data remember things should be read in the form of strings
    String conf_str = Serial.readString();
    
    // The first 4 bytes should be the update rate
    update_rate = (conf_str.substring(0,conf_str.indexOf(','))).toInt();
    
    // Remove the updateRate
    conf_str = conf_str.substring(conf_str.indexOf(',')+1);
    
    // Start of the trigger pins
    int trig_start = conf_str.indexOf("TRI");
    conf_str = conf_str.substring(trig_start+4);
    
    // Now we can seperate the echo and trigger portion
    int ech_start = conf_str.indexOf("ECH");
    
    // Serial.println("ECH_START:: " + String(ech_start));
    String trig_pin_str = conf_str.substring(0,ech_start);
    int comma_index = 0;
    int trig_pin_arr_index = 0;
    
    while (((comma_index = trig_pin_str.indexOf(',')) != -1) && (trig_pin_arr_index < 4)){
      // comma_index indicates the next position
      String trig_pin_value = trig_pin_str.substring(0,comma_index);
      trigPins[trig_pin_arr_index]= trig_pin_value.toInt();
      // Remove the old value from the index
      trig_pin_str = trig_pin_str.substring(comma_index+1);
      trig_pin_arr_index += 1;
    }

    // Reset values for next iteration involving echo pins
    String echo_pin_value= "";
    String echo_pin_str = conf_str.substring(ech_start+4);
    int echo_pin_index =0;
    
    // Now we do the same thing for the echo pins
    while (((comma_index = echo_pin_str.indexOf(','))!= -1) && (echo_pin_index < 4)){
      String ech_pin_value = echo_pin_str.substring(0,comma_index);
      echoPins[echo_pin_index] = ech_pin_value.toInt();
      echo_pin_str = echo_pin_str.substring(comma_index+1);
      echo_pin_index++;
    }
    
    // Do a sanity check to make sure we do indeed have all the values we need to start
    if (echo_pin_str.indexOf('\n') != -1 && echo_pin_index == trig_pin_arr_index){
      // Successfully found the end of the string and it's time to call it a day
      // Calculate the mS runTime
      loop_time_millis = ((1.0)/((float)update_rate))*100;
      
      // Save the configured trig pins
      number_echo_pins = echo_pin_index;
      number_trig_pins = trig_pin_arr_index;
      
      // Save the configured echo pins
      for (int i=0; i < number_echo_pins; i++){
        pinMode(echoPins[i],INPUT);
        pinMode(trigPins[i],OUTPUT);
      }
      return 1;
    }
  }
  // Otherwise we need to reset the Configuration so we know that we are not corrupting Anything
  resetConfigurationToDefault();
  return 0;
}



int findConfHeader(void){
  while(Serial.available() > 0){
    char nextByte;
    Serial.readBytes(&nextByte,1);
    if (state == 0 && nextByte == 'C'){
      state = 1;
    }else if (state == 1 && nextByte == 'O'){
      state += 1;
    }else if (state == 2 && nextByte == 'N'){
      return 1;
    }else{
      state = 0;
    }
  }
  
  // If we get this far we failed
  return 0;
}


void readCommand(void){
  long time = millis();
  command_str += Serial.readString();
  int command_start = 0;
  
  //Serial.println(command_str);
  if ((command_start = command_str.indexOf("REQ")) >= 0){
    command_str = command_str.substring(command_start);
    
    // Find out if we have received the full packet
    int found_comma_index = -1;
    if ((found_comma_index = command_str.indexOf(",")) > -1){
      // Now know we have our data
      String readingNumber = command_str.substring(3,found_comma_index);
      
      // convert to an integer
      int resp_readings = readingNumber.toInt();
      
      Serial.println(String(runTime));
      String responseStr = "REP";
      
      for(int i = 0 ; i < number_echo_pins; i++){
        for (int j=resp_readings ; j >0; j--){
          responseStr += "(";
          responseStr += String(readTimes[i][j]);
          responseStr += ",";
          responseStr += String(readDistances[i][j]);
          responseStr += ")";
        }
      }
      
      Serial.println(responseStr);
      long endTime = millis();
      runTime = endTime-time;
    }
  }
}


void setup() {
  Serial.begin(250000);
  // Indicate we are ready to be configured
  Serial.println("RDY");
  Serial.setTimeout(10);
}




void loop() {
  
  // If we are not configured we stay in this loop
  if (!isConfigured){
    if(readConfiguration()){
      isConfigured = true;
      // Respond with configured
      Serial.println("SUC");
    }
    
  }else{
    // Check if there is a command
    readCommand();
    // Right and then read
    // Set all states to LOW to make sure we are alright
    double newReadings[4];
    unsigned long newTimes[4];
    for (int i=0; i < number_echo_pins; i++){
      digitalWrite(trigPins[i],HIGH);
      delayMicroseconds(10);
      digitalWrite(trigPins[i],LOW);
      long duration = pulseIn(echoPins[i],HIGH);
      newReadings[i] = (duration*HCSRO4_CONSTANT);
      newTimes[i] = (millis()-startTime);
    }
    updateReadingsData(newReadings,newTimes);
  }
}

