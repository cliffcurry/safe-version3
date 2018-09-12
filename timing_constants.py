DISPLAY_ERROR_DELAY=100
DISPLAY_DELAY=5
SHORT_DISPLAY_DELAY=1
RESET_DISPLAY_DELAY=12
WAIT_FOR_SUPERVISOR_TIME=5*60 # five minutes 

SERIAL_TIMEOUT_TIME=10
# timeouts in seconds for  the Arduino serial commands    
ARDUINO_COMMAND_TIMEOUT = 5  # wait 5 seconds for response, before declaring bad communictions
TIME_IT_TAKES_TO_DETECT_SWITCH =20  # wait 20 seconds to measure the impedance, before erroring out
# hardware pins used in the arduino 
DATABASE_TIMEOUT_SECONDS=5 
FAKE_DB_DELAY_TIME=1
DISPLAY_SOFTWARE_VERSION_TIME=4            
CHECK_SWITCH_STATE_DURATION=60 # if they don't turn off the switch after 1 minute, give up 
CHECK_NETWORK_INTERVAL=60
CHECK_OPEN_CLOSED_INTERVAL=30