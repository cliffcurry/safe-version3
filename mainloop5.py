# this is mainloop5.py 
import calculations
import timing_constants
import globs
import timeoutTimer
import SerialConnection
import DataBaseV3
import DataBaseQuery
import DisplayStuff
import tkinter as tk
import ArdCommandResponse
import datetime
import socket
from enum import Enum
class st(Enum):
    IDLE= 11 #  #0   # ready for the card to be swiped
    WAIT_FOR_FIRST_SWIPE= 12 #  #0   # ready for the card to be swiped
    FIRST_PROX_CARD_READ= 13 #  #1   # database has been quiried, waiting for it to respond
    WAIT_TO_RESET= 14 #  #2 
    SECOND_SWIPE_NEEDED= 16 #  #4
    PROCESS_SECOND_SWIPE= 17 #  #8
    CONTINUE_TIMING_ACCESS= 18 #  #5
    EXTEND_TIME_PROMPT= 19 #  #6
    CHECK_SWITCH_STATE= 100 #  #7
    SERIAL_COMMAND_NOT_RESPONDING= 103 #  #12
    IMP_CHECK_FAILED= 104 #  #11
    EXTENDED_ACCESS_SWIPE = 105
    USER_INTERRUPT = 266
    CALC_ACCESS_TIME=272
    SET_TIMER_FOR_SWITCH_DETECT =275
    DATABASE_MISSING_DATA_ERROR =276
    GET_MACHINE_INFO=278
    CHECK_NETWORK_CONNECTED=279
    NO_NETWORK=280
   
def seconds_to_minutes_display(seconds):
    min=seconds//60
    sec=seconds-min*60
    ss=str(sec)
    if len(ss)==1:
        ss='0'+ss
    return str(min)+":"+ss

def minutes_to_seconds(minutes):    
    return minutes*60
    
    
def fill_global_table_from_mac(ddict):
    globs.machineTable['machine_id']=ddict['machine_id']
    globs.machineTable['name']=ddict['name']
    globs.machineTable[ 'lab_containing_machine']=ddict['lab_containing_machine']
    globs.machineTable[ 'kind_of_swipe_needed']=ddict['kind_of_swipe_needed']
    globs.machineTable[ 'start_time']=ddict['start_time'] 
    globs.machineTable[ 'end_time']=ddict['end_time']
    globs.machineTable[ 'minutes_enabled']=ddict['minutes_enabled']
    globs.machineTable[ 'uses_estop']=ddict[ 'uses_estop']

    globs.interlockTable['controller_serial_number']=ddict['controller_serial_number']
    globs.interlockTable['relay_box_serial_number']=ddict['relay_box_serial_number']
    globs.interlockTable['controller_serial_number']=ddict['controller_serial_number']

    globs.labTable['name']=ddict['lab_name']
    globs.labTable['room']=ddict['lab_room']
    globs.labTable['start_time']=ddict['lab_start_time']
    globs.labTable['end_time']=ddict['lab_end_time']    
    
###  here is a diagram of the first part of the state machine    
### <-----------------------------WAIT TO RESET--------------------------------------------------<<<<< -----------------------------|
### |                                <------------LOOP-BASED ON TIMER------ -----|                                       ( denied)->|         
### |                                |                                           ^                                       ( 2nd swipe needed)->SECOND_SWIPE_NEEDED-->
### V                                V                                           ^                                                       (estop) ->  CALC_ACCESS_TIME-->
### -->IDLE-> CHECK_NETWORK_CONNECTED-> GET_MACHINE_INFO-> WAIT_FOR_FIRST_SWIPE->| -->(swipe) --> FIRST_PROX_CARD_READ--> (all_access)-> (no estop)->SET_TIMER_FOR_SWITCH_DETECT-->

# checking to see if the machine power switch is closed or not 
#                                 |<--------------switch on loop ----------------------------------|
#                                 |                                    (sw on)-> IMP_CHECK_FAILED->| 
#                                 |                                    (timer expired) --> WAIT TO RESET
#                                 V  (no estop) --CHECK_SWITCH_STATE--> (sw off)->CALC_ACCESS_TIME-->
# -->SET_TIMER_FOR_SWITCH_DETECT--> (estop) --> CALC_ACCESS_TIME-->  

##  calcuating access and so on .... 
##  using a global flag, called globs.in_extended_time_state, to reuse a lot of the code.  flag is reset in IDLE state. 
## 
##                                                                                                                                             (2nd swipe needed)-->SECOND_SWIPE_NEEDED
##                                                                                                                                             (all is ok)    -->CALC_ACCESS_TIME
##                                                                                                                                             (access deny)  -->WAIT_TO_RESET  ---this is exit from loop
##                                                                                                    (swipe detect)-->EXTENDED_ACCESS_SWIPE-> (card not same)-->WAIT_TO_RESET
##                                               (extended time state)             EXTEND_TIME_PROMPT (no swipe detect)-->WAIT_TO_RESET->
##  CALC_ACCESS_TIME--> CONTINUE_TIMING_ACCESS-->(not extended time state, timed out)--> WAIT_TO_RESET

#  second swipe logic  .... 
#### 
####                                                                                                                     
####                                                                                                                       
####                                                           (ok, not extended time state)-> CALC_ACCESS_TIME                                                           
####                                                           (extended time state) --> SET_TIMER_FOR_SWITCH_DETECT    ---loop for extended time situation                 
####                          (swipe)-> PROCESS_SECOND_SWIPE-> (2nd swipe denied)-> WAIT_TO_RESET    
####  SECOND_SWIPE_NEEDED--> (timeout)-->WAIT_TO_RESET-> 





#------------------------------------------------------------------------------------------------------------------------        
def mainloop(state,first_time_here_flag):
    if (state== st.USER_INTERRUPT):
        if (first_time_here_flag==True):
            SerConn.cardID_available=False; 
            Dis.change_background()
            Dis.display_message_to_user('--User Cancel-- ',1)
            Dis.display_message_to_user('Screen touch detected',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('System restarting',4)
            Dis.display_message_to_user('one moment...',5)
            timeoutTimer1.set_time(timing_constants.DISPLAY_DELAY);
            first_time_here_flag=False   
#-------    
        else:
            globs.user_touched_screen_flag=False  # reset the flag that tells the user interrupted
            if timeoutTimer1.timed_out():
                state=st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag  
    #---------------------------------------------------------
    if (state== st.IDLE):  # is only in this state for the time it takes the Arduino to ack its command
        if (first_time_here_flag==True):
            SerConn.cardID_available=False; 
            globs.in_extended_time_state=False  # this flag is reset at every start 
            Dis.reset_background()
            Dis.display_message_to_user('Starting up...',1)
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            
            print("Sending Arduino message to turn off relay")
            first_time_here_flag=False   
#-------    
        else:
            globs.user_touched_screen_flag=False
            response =ACommandProc.turn_off_device()
            if response==True:
                print('device  is off')
                state= st.CHECK_NETWORK_CONNECTED ; first_time_here_flag=True;
            elif response==False:
                print('ERROR, Device off command Failed ')
                state= st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=True;
        return state,first_time_here_flag  

#-------------------------------------------------------
    if (state== st.CHECK_NETWORK_CONNECTED): # just a message to let one know that the network is active 
        if first_time_here_flag==True:
            first_time_here_flag=False
            timeoutTimer1.set_time(timing_constants.SHORT_DISPLAY_DELAY);
            ipaddress=socket.gethostbyname(socket.gethostname())  # look up the IP address of this device
            if ipaddress=="127.0.0.1":   # it has not been assigned by the router
                print("You are not connected to the internet!")
                state= st.NO_NETWORK; first_time_here_flag=True
            else:  # it has been assigned by the router
                print("You are connected to the internet with the IP address of "+ ipaddress )
                Dis.display_message_to_user('Starting up...',1)
                Dis.display_message_to_user('connected to network',2)
                Dis.display_message_to_user('with an IP of ',3)
                Dis.display_message_to_user(ipaddress, 4)
                Dis.display_message_to_user('',5)
        else:
            if timeoutTimer1.timed_out(): 
                state= st.GET_MACHINE_INFO; first_time_here_flag=True
        return (state,first_time_here_flag)           
        
#-------------------------------------------------------
    if (state== st.NO_NETWORK): # automatic IP address assignment failed on this device
        if first_time_here_flag==True:
            first_time_here_flag=False
            timeoutTimer1.set_time(timing_constants.CHECK_NETWORK_INTERVAL);
                
            Dis.display_message_to_user('NO NETWORK',1)
            
            Dis.display_message_to_user('I will check for ',2)
            Dis.display_message_to_user('network connection in',3)
            Dis.display_message_to_user(' ',4);
            Dis.display_message_to_user('Minutes',5)
          
        else:
            if (timeoutTimer1.secondstick()):
                Dis.display_message_to_user(seconds_to_minutes_display(timeoutTimer1.get_timeleft()),4)
            if timeoutTimer1.timed_out():
                
                state= st.CHECK_NETWORK_CONNECTED; first_time_here_flag=True # go back, in a loop, to see if the network has come back up. 
                
        return (state,first_time_here_flag)           
#------------------------------------------------------
    if (state== st.GET_MACHINE_INFO): # get the machineTable, the machine information
        # this stage just gets the data, moves on.
        if first_time_here_flag==True:
            first_time_here_flag=False;
            Dis.display_message_to_user('Looking up',1)
            Dis.display_message_to_user('machine info',2)
            Dis.display_message_to_user('for interlock mac',3)
            Dis.display_message_to_user(globs.my_mac_address,4)
            Dis.display_message_to_user('in the database ',5);
          
            ####DATABASE QUERY HERE
            ddict=Data.info_from_mac(globs.my_mac_address)  # get the database data
            if ddict!=None:
                fill_global_table_from_mac(ddict)            
            else:
                state=st.DATABASE_MISSING_DATA_ERROR; first_time_here_flag=True; 
        else:
            state= st.WAIT_FOR_FIRST_SWIPE ;first_time_here_flag=True
        return (state,first_time_here_flag)   
#---------------------------------------------------------
    if (state== st.WAIT_FOR_FIRST_SWIPE):
        # STAYS IN a check machine, wait for swipe loop, FOREVER,  until the card is swiped
        if (first_time_here_flag==True):
            SerConn.cardID_available=False; 
            timeoutTimer1.set_time(timing_constants.CHECK_OPEN_CLOSED_INTERVAL);
             # retrieve the on and off times from the table read in GET_MACHINE_INFO, determine if should be open or closed.
            time_now=   calculations.tominutes(datetime.datetime.now())          
            print("time now=",time_now)       
            dev_end_time=min(calculations.tominutes(globs.machineTable["end_time"]),
                                calculations.tominutes(globs.labTable["end_time"]))
            print("end time=",dev_end_time)
            dev_start_time=max(calculations.tominutes(globs.machineTable["start_time"]),
                               calculations.tominutes(globs.labTable["start_time"]))
            print("start time=",dev_start_time)                   
            if (time_now>dev_end_time) or (time_now < dev_start_time): # if closed, let the user know
                print("closed")
                Dis.display_message_to_user('--- Sorry, CLOSED ----',1)
                Dis.change_background()   
            else:  # if not closed, let the user know all is OK 
                Dis.display_message_to_user('SWIPE CARD FOR ACCESS',1)
                Dis.reset_background()
            Dis.display_message_to_user(globs.machineTable["name"],2)
            Dis.display_message_to_user('Hours.. %s to %s'% (globs.machineTable['start_time'],globs.machineTable['end_time']),3)
            Dis.display_message_to_user(globs.labTable["name"],4)
            Dis.display_message_to_user('Hours.. %s to %s'%(globs.labTable['start_time'],globs.labTable['end_time']),5)
            first_time_here_flag=False;
            globs.user_touched_screen_flag=False  # reset screen touch  callback flag 
        else:     # wait here until the card has been swiped or the timer times out. 
            if timeoutTimer1.timed_out():
                state=st.GET_MACHINE_INFO; first_time_here_flag=True;  # loop back on yourself at the timer interval
            if (SerConn.cardID_available):  
                Dis.reset_background()
                globs.first_swipe_prox_card=SerConn.get_cardID()
                Dis.display_message_to_user('Prox='+globs.first_swipe_prox_card,1);
                Dis.display_message_to_user('',2)
                Dis.display_message_to_user('',3)
                Dis.display_message_to_user('',4)
                Dis.display_message_to_user('',5)
                state= st.FIRST_PROX_CARD_READ ; first_time_here_flag=True;
        return (state,first_time_here_flag) 
#---------------------------------------------------------
    if (state== st.FIRST_PROX_CARD_READ): #get the first_swipe_prox_card
        if first_time_here_flag==True:
           
            ddict=Data.info_from_prox(globs.first_swipe_prox_card)
            if ddict != None:
            
                globs.firstSwipePersonTable['university_id']=ddict['university_id']
                globs.firstSwipePersonTable['name']=ddict['name']
                globs.firstSwipePersonTable['kind_of_person']=ddict['kind_of_person']
                globs.firstSwipePersonTable['start_date']=ddict['start_date']
                globs.firstSwipePersonTable['end_date']=ddict['end_date']
                
                globs.firstSwipePersonTable['start_time']=ddict['start_time']
                globs.firstSwipePersonTable['end_time']=ddict['end_time']
                
                
                Dis.display_message_to_user('ID='+globs.firstSwipePersonTable['university_id'],2)
                Dis.display_message_to_user(globs.firstSwipePersonTable['name'],3)
                Dis.display_message_to_user('',4)
                Dis.display_message_to_user('',5)
                timeoutTimer1.set_time(timing_constants.DISPLAY_DELAY);
                first_time_here_flag=False;
            else:
                state=st.DATABASE_MISSING_DATA_ERROR; first_time_here_flag=True
        else:
            if timeoutTimer1.timed_out():
                (OK,globs.first_swipe_reason)=Data.first_swipe(globs.first_swipe_prox_card,globs.my_mac_address)
                print("first swipe result reason=",globs.first_swipe_reason)
                if not OK:  # failed the first swipe test
                    if globs.first_swipe_reason == 'Second swipe needed.': # means passed everything, but 2nd swipe needed. 
                        state= st.SECOND_SWIPE_NEEDED ;  first_time_here_flag=True
                    else : # did not pass, for some fatal reason     
                        Dis.display_message_to_user('ACCESS DENIED',3)
                        Dis.display_message_to_user(globs.first_swipe_reason,4)
                        print("Access denied because of ",globs.first_swipe_reason);
                        state= st.WAIT_TO_RESET;   first_time_here_flag=True  # start all over again
                else: # passed the first swipe test        
                    print("User has access to this machine without supervisor ")
                    state= st.SET_TIMER_FOR_SWITCH_DETECT ;first_time_here_flag=True
                       
               
        return (state,first_time_here_flag)           
        
 
#----------------------------------------------------
    if (state== st.DATABASE_MISSING_DATA_ERROR): # None was returned somewere
        Dis.display_message_to_user('ACCESS DENIED',3)
        Dis.display_message_to_user('because of',4)
        Dis.display_message_to_user('database problem',5)
        state= st.WAIT_TO_RESET; first_time_here_flag=True  # waits in wait to reset state
        return (state,first_time_here_flag)  

#--------------------------------------------------------- 
    if (state== st.SECOND_SWIPE_NEEDED):    
        if (first_time_here_flag==True):
            SerConn.cardID_available=False
            print('notify the user that a second swipe is needed')
            
            Dis.display_message_to_user('SECOND SWIPE REQUIRED',1)
            print(globs.machineTable['kind_of_swipe_needed'])
            Dis.display_message_to_user('For %s'% globs.machineTable['name'],2)
            Dis.display_message_to_user(globs.machineTable['kind_of_swipe_needed'],3);
            Dis.display_message_to_user('swipe is needed' ,4)
            print(' Set the timer to wait for the supervisor swipe');
            timeoutTimer1.set_time(timing_constants.WAIT_FOR_SUPERVISOR_TIME)
            first_time_here_flag=False;   
        #-------
        else:     
            if (timeoutTimer1.secondstick()):
                Dis.display_message_to_user("Waiting for " + seconds_to_minutes_display(timeoutTimer1.get_timeleft()),5)
            if (timeoutTimer1.timed_out()):
                Dis.display_message_to_user('Time for 2nd swipe',1)
                Dis.display_message_to_user('has expired.',2)
                Dis.display_message_to_user('Resetting system.',3);
                Dis.display_message_to_user('Thanks,' ,4)
                Dis.display_message_to_user('Bye!' ,4)
                state= st.WAIT_TO_RESET; first_time_here_flag=True;   
            # check for second swipe from arduino   
            if SerConn.cardID_available:
                timeoutTimer1.reset()
                print('second swipe detected')
                ### GET second swipe from the Arduino 
                globs.second_swipe_prox_card=SerConn.get_cardID()
                Dis.display_message_to_user('Prox Card ID ',1)
                Dis.display_message_to_user(globs.second_swipe_prox_card,2)
                if globs.machineTable['kind_of_swipe_needed']=="supervisor":
                    Dis.display_message_to_user('as supervisor',3)
                elif globs.machineTable['kind_of_swipe_needed']=="two students": 
                    Dis.display_message_to_user('as 2nd student',3)
                Dis.display_message_to_user('',4)
                Dis.display_message_to_user('',5)
                state= st.PROCESS_SECOND_SWIPE ; first_time_here_flag=True;          
        return state,first_time_here_flag 
#--------------------------------------------------------------              
    if (state== st.WAIT_TO_RESET):    # simply waits for a display delay so user can read message, then goes to st.IDLE
        if (first_time_here_flag==True):
            first_time_here_flag=False;
            timeoutTimer1.set_time(timing_constants.RESET_DISPLAY_DELAY)
            Dis.change_background()
        #---------    
        else:    
            if (timeoutTimer1.timed_out()):
                state= st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag 
#--------------------------------------------------------------              
    if (state== st.PROCESS_SECOND_SWIPE):    
        if (first_time_here_flag==True):
            first_time_here_flag=False;
            ### look up the second person in the database
            ddict=Data.info_from_prox(globs.second_swipe_prox_card)
            if ddict != None:
                globs.secondSwipePersonTable['university_id']=ddict['university_id']
                globs.secondSwipePersonTable['name']=ddict['name']
                globs.secondSwipePersonTable['kind_of_person']=ddict['kind_of_person']
                globs.secondSwipePersonTable['start_date']=ddict['start_date']
                globs.secondSwipePersonTable['end_date']=ddict['end_date']
                
                globs.secondSwipePersonTable['start_time']=ddict['start_time']
                globs.secondSwipePersonTable['end_time']=ddict['end_time']
                Dis.display_message_to_user(globs.secondSwipePersonTable['name'],4)
                timeoutTimer1.set_time(timing_constants.DISPLAY_DELAY);
            else:
                state=st.DATABASE_MISSING_DATA_ERROR; first_time_here_flag=True
    #--------           
        else:
            if timeoutTimer1.timed_out():
                (OK,globs.second_swipe_reason)=Data.second_swipe(globs.first_swipe_prox_card,globs.second_swipe_prox_card,globs.my_mac_address)
                print('Second swipe reason=',globs.second_swipe_reason)
                if OK:  # turn on the device 
                    print('In extended time=',globs.in_extended_time_state)
                    print('so device will be turned on ')
                    if globs.in_extended_time_state: # only place extended this flag is checked!!
                        state=st.CALC_ACCESS_TIME;first_time_here_flag=True
                    else:
                        state= st.SET_TIMER_FOR_SWITCH_DETECT ;first_time_here_flag=True
                else: # not OK 
                    Dis.display_message_to_user('Denied',4)
                    Dis.display_message_to_user(globs.second_swipe_reason,5)
                    state= st.WAIT_TO_RESET; first_time_here_flag=True;     
        return(state,first_time_here_flag);
#----------------------------------------------------------------
#        turm on the device and calc access time too    
    if (state== st.CALC_ACCESS_TIME):        # display message to the user, send a message to the arduino to turn the device on 
        if (first_time_here_flag==True):
           
            # calculate the on and off times 
            print("time now=",calculations.tominutes(datetime.datetime.now()))       
            globs.actual_end_time=min(calculations.tominutes(globs.machineTable["end_time"]),
                                calculations.tominutes(globs.firstSwipePersonTable["end_time"]),
                                calculations.tominutes(globs.labTable["end_time"]))
            print("actual end time=",globs.actual_end_time)
            globs.actual_start_time=max(calculations.tominutes(globs.machineTable["start_time"]),
                                calculations.tominutes(globs.firstSwipePersonTable["start_time"]),
                                calculations.tominutes(globs.labTable["start_time"]))
            globs.user_access_minutes=calculations.time_for_access(globs.actual_start_time, 
                        globs.actual_end_time,int(globs.machineTable["minutes_enabled"]))
            if globs.firstSwipePersonTable["kind_of_person"]=="all access":
                globs.user_access_minutes=60*12 # all access people get 12 hours of operation. 
            timeoutTimer1.set_time(minutes_to_seconds(globs.user_access_minutes));
            print("Setting timeout timer to ",globs.user_access_minutes," minutes")
           
            print("Sending Arduino message to turn on device")
            first_time_here_flag=False
    #-------            
        else: 
            response=ACommandProc.turn_on_device()
            if response==False:
                    print('ERROR in arduino request to turn on the device  ')
                    state= st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=True;
            elif response==True:
                    print('device  is on ')
                    state=st.CONTINUE_TIMING_ACCESS; first_time_here_flag=True
        return state,first_time_here_flag 
        
#----------------------------------------------------------------        
    if (state== st.CONTINUE_TIMING_ACCESS):        # display the message to the user, time the access, respond to user interrupt
        if (first_time_here_flag==True):
            Dis.display_message_to_user(globs.firstSwipePersonTable["name"],1)
            Dis.display_message_to_user('Has access for',2)
           
            timeoutTimer1.set_time(minutes_to_seconds(globs.user_access_minutes));
            Dis.display_message_to_user(seconds_to_minutes_display(minutes_to_seconds(globs.user_access_minutes)),3);
            Dis.display_message_to_user('Minutes',4)
            Dis.display_message_to_user('',5)
            globs.user_touched_screen_flag=False    # reset any touches that may have happened before now 
            first_time_here_flag=False
    #-------            
        else: 
            if globs.user_touched_screen_flag==True: # checked in 3 places: cont.tim.access, ext.time.prompt, sup.need.ext 
                state=st.USER_INTERRUPT ; first_time_here_flag=True   # if so, reset system to start
                print(" Checking flag indicates that the User has interrrupted loop");                        
            if (timeoutTimer1.secondstick()):
                Dis.display_message_to_user(seconds_to_minutes_display(timeoutTimer1.get_timeleft()),3)
            if (timeoutTimer1.get_timeleft()<=minutes_to_seconds(globs.user_access_minutes)//5):
                    state= st.EXTEND_TIME_PROMPT; first_time_here_flag=True
            if (timeoutTimer1.timed_out()):
                Dis.display_message_to_user('Your time',2)
                Dis.display_message_to_user('is up. ',3)
                Dis.display_message_to_user('Thanks, ',4)
                Dis.display_message_to_user('Bye! ',4)
                state= st.WAIT_TO_RESET; first_time_here_flag=True;        
        return state,first_time_here_flag         
#----------------------------------------------------------------        
    if (state== st.EXTEND_TIME_PROMPT):    #  from st.CONTINUE_TIMING_ACCESS. look for avaliabilty of a card swipe from reader       
        if (first_time_here_flag==True):
            first_time_here_flag=False
            SerConn.cardID_available=False
            Dis.display_message_to_user('Swipe to extend access ',5)
            timeoutTimer1.set_time(minutes_to_seconds(globs.user_access_minutes)//5)   
        #----    
        else: 
            if (timeoutTimer1.secondstick()):
                Dis.display_message_to_user(seconds_to_minutes_display(timeoutTimer1.get_timeleft()),3)
            if globs.user_touched_screen_flag==True: # checked in 3 places: cont.tim.access, ext.time.prompt, sup.need.ext
                    state=st.USER_INTERRUPT ; first_time_here_flag=True
                    globs.user_touched_screen_flag=False
                    print(" Checking flag indicates that the User has interrrupted loop");                
            if (SerConn.cardID_available):
                state= st.EXTENDED_ACCESS_SWIPE ; first_time_here_flag=True;
            if (timeoutTimer1.timed_out()):
                Dis.display_message_to_user('Your time',2)
                Dis.display_message_to_user('is up. ',3)
                Dis.display_message_to_user('Thanks, ',4)
                Dis.display_message_to_user('Bye! ',4)
                state= st.WAIT_TO_RESET; first_time_here_flag=True;  
        return state,first_time_here_flag 
 #----------------------------------------------------------------        
    if (state== st.EXTENDED_ACCESS_SWIPE):        # got a swipe, need to check it to see if it is from the same card as before 
        cardID=SerConn.get_cardID()         # already know data is available, now get the info 
        Dis.display_message_to_user('Prox= %s' % cardID,1);
        if cardID != globs.first_swipe_prox_card: # if not same card, error out 
            Dis.display_message_to_user('Is not the ID ',2)
            Dis.display_message_to_user('used previously.',3)
            Dis.display_message_to_user('Access Denied',4)
            Dis.display_message_to_user('Restarting...',5)
            state= st.WAIT_TO_RESET; first_time_here_flag=True;
         
        else:   # same card as before .  Note that the user has been qualified before
            ## qualify the user again, just in case something has changed in the database in the past few minutes 
            (OK,extended_swipe_reason)=Data.first_swipe(globs.first_swipe_prox_card,globs.my_mac_address)
            print("Extended swipe result reason=",extended_swipe_reason)
            if not OK:  # failed the first swipe test
                if extended_swipe_reason == 'Second swipe needed.': # means passed everything, but 2nd swipe needed. 
                    globs.in_extended_time_state=True  # set this flag 
                    state= st.SECOND_SWIPE_NEEDED ;  first_time_here_flag=True
                else : # did not pass, for some fatal reason     
                    Dis.display_message_to_user('ACCESS DENIED',3)
                    Dis.display_message_to_user(extended_swipe_reason,4)
                    print("Access denied because of ",extended_swipe_reason);
                    state= st.WAIT_TO_RESET;   first_time_here_flag=True  # start all over again
            else: # passed the first swipe test   
                # machine is on now, do not do any testing for switch on             
                state=st.CALC_ACCESS_TIME; first_time_here_flag=True

        
        return state,first_time_here_flag     
 #----------------------------------------------------------------        
   
# -------------------------------------------------------
   
#--------------------------------------------------------------              
    if (state== st.SET_TIMER_FOR_SWITCH_DETECT):     # simply starts a timeout timer, that's all.  this timer limits the time 
        if (first_time_here_flag==True):             # the program will wait for the user to turn off the switch 
            timeoutTimer1.set_time(timing_constants.CHECK_SWITCH_STATE_DURATION)  # timer 1 is used to time the overall switch turn off time 
            first_time_here_flag=False
        else:
            state= st.CHECK_SWITCH_STATE; first_time_here_flag=True 
        return(state,first_time_here_flag);
#----------------------------------------------------------------        
    if (state== st.CHECK_SWITCH_STATE):           # if using estop, just turn on the device. 
        if (first_time_here_flag==True):          # else, let the user know we are checking the power switch, then wait for the arduino to return the impedance
            first_time_here_flag=False
            if globs.machineTable["uses_estop"]:
                state= st.CALC_ACCESS_TIME; first_time_here_flag=True;
            else:
                print("Doing impedance measurement")
                Dis.display_message_to_user('',3)
                Dis.display_message_to_user('Checking switch',4)
                Dis.display_message_to_user("Waiting for " + seconds_to_minutes_display(timeoutTimer1.get_timeleft()),5)
        else:        
        #-------         
            (OK,val) = ACommandProc.complete_impedance_measure()     # This commmand takes some time to finish 
            if (timeoutTimer1.secondstick()):
                    Dis.display_message_to_user("Waiting for " + seconds_to_minutes_display(timeoutTimer1.get_timeleft()),5)
            if OK==False:
                print('ERROR in measuring impedance ')
                state=st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=False
            if OK==True:
                print('Impedance measurement is finished, value= ',val)
                if val>5000:
                    state= st.CALC_ACCESS_TIME; first_time_here_flag=True;   # switch is off, so turn the device on 
                    print("And that is considered OFF")
                else:
                    state= st.IMP_CHECK_FAILED; first_time_here_flag=True;      # switch is on, so let the user know
                    print("And that is considered ON")
        return state,first_time_here_flag             

#----------------------------------------------------------------          
    if (state== st.IMP_CHECK_FAILED):                               # tell the user to turn off the switch. wait for a short time so the user can read the info 
        if (first_time_here_flag==True):                            #  also check the timer to see if the time allowed for the user to turn the switch is expired 
            first_time_here_flag=False
            Dis.change_background()
            print("Here because of failed impedance test")
            print("Tell user to turn off the power switch")
            Dis.display_message_to_user('On switch detected',3)
            Dis.display_message_to_user('Turn Off switch',4)
            Dis.display_message_to_user("Waiting for " + seconds_to_minutes_display(timeoutTimer1.get_timeleft()),5)
            timeoutTimer2.set_time(timing_constants.DISPLAY_DELAY)    # timer 2 is used only to time this message duration. 
#-------            
        else: 
            if (timeoutTimer1.secondstick()):
                Dis.display_message_to_user("Waiting for " + seconds_to_minutes_display(timeoutTimer1.get_timeleft()),5)     
            if timeoutTimer1.timed_out():           # timer 1 is used to time the overall switch detection process
                Dis.display_message_to_user('Resetting system',1)
                Dis.display_message_to_user('Because machine',2)
                Dis.display_message_to_user('power switch is ',3)
                Dis.display_message_to_user('still on ',4)
                Dis.display_message_to_user(' ',5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True            
            elif  (timeoutTimer2.timed_out()):      # timer 2 is used to time the display of this particular message
                Dis.reset_background()
                state= st.CHECK_SWITCH_STATE; first_time_here_flag=True 
        return state,first_time_here_flag            
#----------------------------------------------------------------          
    if (state== st.SERIAL_COMMAND_NOT_RESPONDING):        
        if (first_time_here_flag==True):
            print("Here Because the arduino was sent a command and it did not respond")
            Dis.change_background()
            Dis.display_message_to_user('COMMUNICATION ERROR',4)
            timeoutTimer1.set_time(timing_constants.DISPLAY_ERROR_DELAY)
            print("This is just a delay state so the user can read the message")
            print('Send an arduino message to turn the relay off')
            
            first_time_here_flag=False
        OK=ACommandProc.turn_off_device()
        if OK==False:
            print('error in arduino request to turn off device ')
                
        if  timeoutTimer1.timed_out():
            Dis.reset_background()
            state= st.IDLE; first_time_here_flag=True                    
        return state,first_time_here_flag    



        
if  __name__ == "__main__":     

   
    SerConn=SerialConnection.SerialClass()
    stophere=True
    while stophere:    # wait here for the arduino to reset and start sending stuff
        SerConn.attempt_to_get_readings(); 
        if SerConn.cardID_available:
            print("cardID=",SerConn.get_cardID())
        if SerConn.alive_available:
            print("alive=",SerConn.get_alive()) 
            stophere=False # an alive message means the arduinois awakened
    ACommandProc=ArdCommandResponse.ArdCommandResponse(SerConn)
    db=DataBaseV3.DataBase()  # 
    Data=DataBaseQuery.DataBaseQuery(db)  # defines the interface to the database
    timeoutTimer1=timeoutTimer.timeoutTimer()   # instantiate one timer
    timeoutTimer2=timeoutTimer.timeoutTimer()   # instantiante another timer
    displayscreen = tk.Tk()                     # set up the TK interface
    displayscreen.overrideredirect(True)         # tell it to be full screen
    Dis=DisplayStuff.Display(displayscreen);     # start the display, creating a single big text area
    timeoutTimer1.set_time(timing_constants.DISPLAY_SOFTWARE_VERSION_TIME)   # delay for a few seconds so the user can read the software version 
    while not timeoutTimer1.timed_out():
        pass
    GlobalState= st.IDLE   # intialize the first state 
    print("initial state=",GlobalState)
    flag=True
    while True:
        displayscreen.update_idletasks()  # call tk loop update function
        displayscreen.update()             # call tk loop update function
        SerConn.attempt_to_get_readings();  # check for serial data coming in from the arduino 
        #if flag:
            #print("STATE=",GlobalState)
        (s,f)=mainloop(GlobalState,flag);   # based on the current state, perform whatever activity is needed. 
        
        if f:
            print("newstate=",s)    # a set flag will cause the new state to be printed
        (GlobalState,flag) = (s,f)   
        
                
                
