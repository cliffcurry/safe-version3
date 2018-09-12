# this is mainloop3.py 
import calculations
import timing_constants
import globs
import timeoutTimer
import SerialConnection
import DataBaseV2
import DataBaseQuery
import DisplayStuff
import tkinter as tk
import ArdCommandResponse
import datetime
from enum import Enum
class st(Enum):
    IDLE= 11 #  #0   # ready for the card to be swiped
    WAIT_FOR_FIRST_SWIPE= 12 #  #0   # ready for the card to be swiped
    FIRST_PROX_CARD_READ= 13 #  #1   # database has been quiried, waiting for it to respond
    WAIT_TO_RESET= 14 #  #2 
    DATABASE_QUERY_TIMED_OUT= 15 #  #3
    SUPERVISOR_NEEDED_CARD= 16 #  #4
    PROCESS_SECOND_SWIPE= 17 #  #8
    CONTINUE_TIMING_ACCESS= 18 #  #5
    START_TIMING_ACCESS= 180 #  #5
    EXTEND_TIME_PROMPT= 19 #  #6
    CHECK_SWITCH_STATE= 100 #  #7
    CHECK_SWITCH_STATE_IMP_MEAS= 101 #  #9
    POWER_SWITCH_CLOSED= 102 #  #10
    SERIAL_COMMAND_NOT_RESPONDING= 103 #  #12
    IMP_CHECK_FAILED= 104 #  #11
    EXTENDED_ACCESS_SWIPE = 105
    WRONG_ID_SWIPE = 106
    SUPERVISOR_NEEDED_EXTENDED =107
    PROX_SWIPE_FROM_SUPER_OBTAINED =109
    USER_INTERRUPT = 266
    GOT_USERS_ID = 267
    GOT_SUPER_ID =268
    GOT_SUPER_TABLE =269
    FIRST_SWIPE_DECISIONS =270
    GOT_MACHINE_ID =271
    
    GOT_MACHINE_TABLE =272
    GOT_USER_TABLE =273
    SUPERVISOR_NEEDED_LOOKUP_NAME=274
    SET_TIMER_FOR_SWITCH_DETECT =275
    DATABASE_MISSING_DATA_ERROR =276
   
def minutes_display(seconds):
    min=seconds//60
    sec=seconds-min*60
    return str(min)+":"+str(sec)

        
def mainloop(state,first_time_here_flag):
    if (state== st.USER_INTERRUPT):
        if (first_time_here_flag==True):
            SerConn.cardID_available=False; 
            Dis.display_message_to_user('User Cancel ',1)
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            timeoutTimer1.set_time(timing_constants.DISPLAY_DELAY);
            first_time_here_flag=False   
#-------    
        else:
            globs.user_touched_screen_flag=False  # reset the flag that tells the user interrupted
            if timeoutTimer1.timed_out():
                state=st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag  
    #---------------------------------------------------------
    if (state== st.IDLE):
        if (first_time_here_flag==True):
            SerConn.cardID_available=False; 
            Dis.display_message_to_user('Swipe card for Access',1)
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
                state= st.WAIT_FOR_FIRST_SWIPE; first_time_here_flag=True;
            elif response==False:
                print('ERROR, Device off command Failed ')
                state= st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=True;
        return state,first_time_here_flag  
    #---------------------------------------------------------
    if (state== st.WAIT_FOR_FIRST_SWIPE):
        if (first_time_here_flag==True):
            SerConn.cardID_available=False; 
            Dis.display_message_to_user('Swipe card for Access',1)
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            first_time_here_flag=False;
        globs.user_touched_screen_flag=False  # reset screen touch  callback flag 
        if (SerConn.cardID_available):  # WAIT FOREVER here until the card is swiped
            globs.first_swipe_prox_card=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID',1);
            Dis.display_message_to_user(globs.first_swipe_prox_card,2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            state= st.FIRST_PROX_CARD_READ ; first_time_here_flag=True;
        return (state,first_time_here_flag) 
    #---------------------------------------------------------
    if (state== st.FIRST_PROX_CARD_READ): #get the first_swipe_prox_card
        if first_time_here_flag==True:
           first_time_here_flag=False;
        else:
            (OK,globs.first_swipe_prox_card)=Data.proxcardlookup(globs.first_swipe_prox_card)
            if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
            elif OK==True:
                print('finished with a good result, ',globs.first_swipe_prox_card)
                Dis.display_message_to_user('ID='+str(globs.first_swipe_prox_card),3)
                if globs.first_swipe_prox_card==None:
                    state= st.DATBASE_MISSING_DATA_ERROR; first_time_here_flag=True 
                else: 
                    state= st.GOT_USERS_ID ;first_time_here_flag=True
        return (state,first_time_here_flag)           
        
        
#---------------------------------------------------------
    if (state== st.GOT_USERS_ID): #get the machine ID
        if first_time_here_flag==True:
           first_time_here_flag=False;
        else:
            (OK,globs.machineID)=Data.interlocklookup(globs.my_mac_address))
            if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
            elif OK==True:
                print('finished with a good result, machineID= ',globs.machineID)
                if globs.machineID==None:
                    state= st.DATBASE_MISSING_DATA_ERROR; first_time_here_flag=True 
                else: 
                    state= st.GOT_MACHINE_ID ;first_time_here_flag=True
        return (state,first_time_here_flag)   

#------------------------------------------------------
    if (state== st.GOT_MACHINE_ID): # get the machineTable, the machine information
        if first_time_here_flag==True:
           first_time_here_flag=False;
        else:
            (OK,globs.machineTable)=Data.machineInfo(globs.machineID)
            if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
            elif OK==True:
                print('finished with a good result, machineTable=',globs.machineTable)

                Dis.display_message_to_user("Machine="+globs.machineTable["name"],4)
                state= st.GOT_MACHINE_TABLE ;first_time_here_flag=True
        return (state,first_time_here_flag)   

#------------------------------------------------------
    if (state== st.GOT_MACHINE_TABLE): # get the firstSwipePersonTable, the user information
        if first_time_here_flag==True:
           first_time_here_flag=False;
        else:
            (OK,globs.firstSwipePersonTable)=Data.personInfo(globs.first_swipe_prox_card)
            if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
            elif OK==True:
                print('finished with a good result, firstSwipePersonTable= ',globs.firstSwipePersonTable)
                Dis.display_message_to_user(globs.firstSwipePersonTable["name"],3)
                state= st.GOT_USER_TABLE ;first_time_here_flag=True
        return (state,first_time_here_flag)   
        
 #----------------------------------------------------
    if (state== st.DATABASE_MISSING_DATA_ERROR): # None was returned somewere
        if first_time_here_flag==True:
                Dis.display_message_to_user('ACCESS DENIED',3)
                Dis.display_message_to_user('because of',4)
                Dis.display_message_to_user('DATABASE: no data',5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True  
                return (state,first_time_here_flag)  
        else:  
                first_time_here_flag=False;

        return (state,first_time_here_flag)          
                
        
 #----------------------------------------------------
    if (state== st.GOT_USER_TABLE): # get the labTable, the information about the labratory
        if first_time_here_flag==True:
           first_time_here_flag=False;
        else:
           
            (OK,globs.labTable)=Data.labInfo(globs.machineTable["lab"])
            if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
            elif OK==True:
                print('finished with a good result, labTable= ',globs.labTable)
		
                state= st.FIRST_SWIPE_DECISIONS ;first_time_here_flag=True
        return (state,first_time_here_flag)          
                

#---------------------------------------------------------
    if (state== st.FIRST_SWIPE_DECISIONS):  # now we have all we need, start to decide some things...
        if first_time_here_flag==True:
           first_time_here_flag=False;
        else:
            print("time now=",calculations.tominutes(datetime.datetime.now()))       
            globs.actual_end_time=min(calculations.tominutes(globs.machineTable["end_time"]),
                                calculations.tominutes(globs.firstSwipePersonTable["end_time"]),
                                calculations.tominutes(globs.labTable["end_time"]))
            print("actual end time=",globs.actual_end_time)
            globs.actual_start_time=max(calculations.tominutes(globs.machineTable["start_time"]),
                                calculations.tominutes(globs.firstSwipePersonTable["start_time"]),
                                calculations.tominutes(globs.labTable["start_time"]))
            print("actual start time=",globs.actual_start_time)
            globs.user_name=globs.firstSwipePersonTable["name"]
            if (globs.user_name==None):
                Dis.display_message_to_user('ACCESS DENIED',3)
                Dis.display_message_to_user('because of',4)
                Dis.display_message_to_user('Unrecognized ID',5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True  
                return (state,first_time_here_flag)  
            else:
                Dis.display_message_to_user(globs.user_name,1)
                if globs.firstSwipePersonTable["kind_of_person"]=="allAccess":
                    if globs.machineTable["uses_estop"]:
                        state=st.CALC_ACCESS_TIME; first_time_here_flag=True
                        return (state,first_time_here_flag)
                    else: 
                        state= st.SET_TIMER_FOR_SWITCH_DETECT ;first_time_here_flag=True
                        return (state,first_time_here_flag)
                (access,reason)=calculations.nonsupervisor_access(globs.actual_start_time,
                                            globs.actual_end_time,globs.first_swipe_prox_card,globs.machineTable["personAccessList"],
                                            globs.machineTable["kind_of_swipe_needed"])
                if access==False and reason != "Supervisor Swipe Needed":      
                        Dis.display_message_to_user('ACCESS DENIED',3)
                        if (reason):
                            Dis.display_message_to_user(reason,4)
                        else:
                            Dis.display_message_to_user('Unknown reason ',4)
                        state= st.WAIT_TO_RESET;   first_time_here_flag=True 
                if access==False and reason=="Supervisor Swipe Needed": 
                    state= st.SUPERVISOR_NEEDED_CARD ;  first_time_here_flag=True
                    return (state,first_time_here_flag)      
                if access==True:
                    if globs.machineTable["uses_estop"]:
                        state=st.CALC_ACCESS_TIME; first_time_here_flag=True
                        return (state,first_time_here_flag)
                    else: 
                        state= st.SET_TIMER_FOR_SWITCH_DETECT ;first_time_here_flag=True
                        return (state,first_time_here_flag)
        return (state,first_time_here_flag)           
    #--------------------------------------------------------------  

    
    if (state== st.SUPERVISOR_NEEDED_CARD):    
        if (first_time_here_flag==True):
            SerConn.cardID_available=False
            Dis.display_message_to_user('Supervisor req.',2);
            Dis.display_message_to_user('Ask the supervisor',3)
            Dis.display_message_to_user('to swipe card',4)
            timeoutTimer1.set_time(timing_constants.WAIT_FOR_SUPERVISOR_TIME)
            first_time_here_flag=False;   
#-------
        else:     
            if (timeoutTimer1.secondstick()):
                Dis.display_message_to_user("Waiting for " + minutes_display(timeoutTimer1.get_timeleft()),5)
            if (timeoutTimer1.timed_out()):
               state= st.IDLE ; first_time_here_flag=True;          
            if SerConn.cardID_available:
                timeoutTimer1.reset()
                globs.supervisor_cardID=SerConn.get_cardID()
                Dis.display_message_to_user('Prox Card ID ',1)
                Dis.display_message_to_user(globs.supervisor_cardID,2)
                Dis.display_message_to_user('as supervisor',3)
                Dis.display_message_to_user('',4)
                Dis.display_message_to_user('',5)
                state= st.PROCESS_SECOND_SWIPE ; first_time_here_flag=True;          
        return state,first_time_here_flag 

    #--------------------------------------------------------------        
    if (state== st.DATABASE_QUERY_TIMED_OUT):    
        if (first_time_here_flag==True):
            Dis.display_message_to_user('Trouble Connecting ',1);
            Dis.display_message_to_user('to Database',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('Not responding',4)
            Dis.display_message_to_user('To query',5)
            first_time_here_flag=False;
        state= st.WAIT_TO_RESET; first_time_here_flag=True;
        return state,first_time_here_flag 
#--------------------------------------------------------------              
    if (state== st.WAIT_TO_RESET):    
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(timing_constants.DISPLAY_DELAY)
            first_time_here_flag=False;
        if (timeoutTimer1.timed_out()):
            state= st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag 
    #--------------------------------------------------------------              
    if (state== st.PROCESS_SECOND_SWIPE):    
        if (first_time_here_flag==True):
            first_time_here_flag=False
       
 #--------           
        (OK,globs.second_swipe_prox_card)=Data.proxcardlookup(globs.supervisor_cardID)
        if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
        elif OK==True:
                print('finished with a good result, supervisor person ID= ',globs.second_swipe_prox_card)
                state= st.GOT_SUPER_ID ;first_time_here_flag=True
        return(state,first_time_here_flag);
 #--------------------------------------------------------------              
    if (state== st.GOT_SUPER_ID):    
        if (first_time_here_flag==True):
            first_time_here_flag=False
       
 #--------               
        else:
            (OK,globs.secondSwipePersonTable)=Data.personInfo(globs.second_swipe_prox_card)
            if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
            elif OK==True:
                print('finished with a good result, supervisor Table Information=',globs.secondSwipePersonTable)
                state= st.GOT_SUPER_TABLE ;first_time_here_flag=True
        return (state,first_time_here_flag)  

#--------------------------------------------------------------              
    if (state== st.GOT_SUPER_TABLE):    
        if (first_time_here_flag==True):
            first_time_here_flag=False
       
 #--------               
        else:
            (ok,reason)=calculations.determine_supervisor_access(globs.first_swipe_prox_card,globs.second_swipe_prox_card,globs.actual_start_time,
                                globs.actual_end_time,globs.machineTable["personAccessList"],globs.machineTable["supervisorAccessList"],
                                globs.machineTable["kind_of_swipe_needed"])
            if ok:
                if globs.machineTable["uses_estop"]:
                    state=START_TIMING_ACCESS;first_time_here_flag=True
                else:
                    state= st.SET_TIMER_FOR_SWITCH_DETECT ;first_time_here_flag=True
            else:
                
                Dis.display_message_to_user('Denied',4)
                Dis.display_message_to_user(reason,5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True;                   
        return state,first_time_here_flag 
    #----------------------------------------------------------------
#        calculate the time of access here, too    
    if (state== st.CALC_ACCESS_TIME):        # display message to the user, send a message to the arduino to turn the device on 
        if (first_time_here_flag==True):
            Dis.display_message_to_user(globs.firstSwipePersonTable["name"],1)
            Dis.display_message_to_user('Has access for',2)
            globs.user_time_of_access=calculations.time_for_access(globs.actual_start_time, 
                        globs.actual_end_time,globs.machineTable["minutes_enabled"])
            if globs.firstSwipePersonTable["kind_of_person"]=="allAccess":
                globs.user_time_of_access=60*12 # all access people get 12 hours of operation. 
            timeoutTimer1.set_time(globs.user_time_of_access*60);
            Dis.display_message_to_user(minutes_display(globs.user_time_of_access),3);
            Dis.display_message_to_user('Minutes',4)
            Dis.display_message_to_user('',5)
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
    if (state== st.CONTINUE_TIMING_ACCESS):        # re-display the message to the user, time the access, respond to user interrupt
        if (first_time_here_flag==True):
            Dis.display_message_to_user(globs.firstSwipePersonTable["name"],1)
            Dis.display_message_to_user('Has access for',2)
           
            timeoutTimer1.set_time(globs.user_time_of_access*60);
            Dis.display_message_to_user(minutes_display(globs.user_time_of_access),3);
            Dis.display_message_to_user('Minutes',4)
            Dis.display_message_to_user('',5)
         
            first_time_here_flag=False
#-------            
        else: 
            if globs.user_touched_screen_flag==True: # check here to see if the user wants to end use of the device 
                state=st.USER_INTERRUPT ; first_time_here_flag=True   # if so, reset system to start
                print(" Checking flag indicates that the User has interrrupted loop");                        
            if (timeoutTimer1.secondstick()):
                Dis.display_message_to_user(minutes_display(timeoutTimer1.get_timeleft()),3)
            if (timeoutTimer1.get_timeleft()<=globs.user_time_of_access//5):
                    state= st.EXTEND_TIME_PROMPT; first_time_here_flag=True
            if (timeoutTimer1.timed_out()):
                state= st.IDLE; first_time_here_flag=True;        
        return state,first_time_here_flag         
    #----------------------------------------------------------------        
    if (state== st.EXTEND_TIME_PROMPT):    # look for avaliabilty of a card swipe from reader       
        if (first_time_here_flag==True):
            SerConn.cardID_available=False
            Dis.display_message_to_user('Swipe to extend access ',5)
            timeoutTimer1.set_time(globs.user_time_of_access*60//5)
            first_time_here_flag=False
        #----    
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user(minutes_display(timeoutTimer1.get_timeleft()),3)
        if globs.user_touched_screen_flag==True:
                state=st.USER_INTERRUPT ; first_time_here_flag=True
                globs.user_touched_screen_flag=False
                print(" Checking flag indicates that the User has interrrupted loop");                
        if (SerConn.cardID_available):
            state= st.EXTENDED_ACCESS_SWIPE ; first_time_here_flag=True;
        if (timeoutTimer1.timed_out()):
            state= st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag 
 #----------------------------------------------------------------        
    if (state== st.EXTENDED_ACCESS_SWIPE):        # got a swipe, need to check it to see if it is from the same card as before 
        if  first_time_here_flag==True:
            cardID=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID',1);
            Dis.display_message_to_user(cardID,2)
            if cardID != globs.first_swipe_prox_card: # if not same card, error out 
                state=st.WRONG_ID_SWIPE;first_time_here_flag=True;
            else:   # same card as before 
                if globs.machineTable["kind_of_swipe_needed"]=="supervisor": # does the machine require supervisor swipe? 
                    state=st.SUPERVISOR_NEEDED_LOOKUP_NAME;first_time_here_flag=True;  
                else:  ## user does not need supervisor here 

                    state=st.CALC_ACCESS_TIME; first_time_here_flag=True;   # if same card was used, and machine does not require supervisor swipe, extend the time. 
        return state,first_time_here_flag     
 #----------------------------------------------------------------        
    if (state== st.WRONG_ID_SWIPE):        
        if (first_time_here_flag==True):
            Dis.display_message_to_user('Is not the ID ',3)
            Dis.display_message_to_user('used previously.',4)
            Dis.display_message_to_user('Access Denied',5)
            timeoutTimer1.set_time(timing_constants.DISPLAY_DELAY)
            first_time_here_flag=False;        
        if (timeoutTimer1.timed_out()):
            state= st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag           
# -------------------------------------------------------
    if (state== st.SUPERVISOR_NEEDED_LOOKUP_NAME):     #  find the name of one of the supervisiors, for use in the display 
        if (first_time_here_flag==True):
            globs.a_supervisorID= globs.machineTable["supervisorAccessList"][0]
            first_time_here_flag=False;   
#-------     
        (OK,sTable)=Data.personInfo(globs.a_supervisorID)
        if OK==False:
            print('finished with an error, let the database guys know')  
            state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
        elif OK==True:
            print('finished with a good result, Table Information about one of the supervisors=',sTable)
            globs.a_supervisor_name=sTable['name']
            state=st.SUPERVISOR_NEEDED_EXTENDED;first_time_here_flag=True;  
        return state,first_time_here_flag     
#---------------------------------------------------------
    if (state== st.SUPERVISOR_NEEDED_EXTENDED):     #  llok for a card swipe, also look for user interrupt 
        if (first_time_here_flag==True):
            SerConn.cardID_available=False
            Dis.display_message_to_user('OK, Supervisor required',2);
            Dis.display_message_to_user('Ask '+globs.a_supervisor_name,3)
            Dis.display_message_to_user('to swipe card',4)
            timeoutTimer1.set_time(timing_constants.WAIT_FOR_SUPERVISOR_TIME)
            first_time_here_flag=False;   
#-------            
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user("Waiting for " + minutes_display(timeoutTimer1.get_timeleft()),5)
        if (timeoutTimer1.timed_out()):
           state= st.IDLE ; first_time_here_flag=True;      
        if globs.user_touched_screen_flag==True:
            state=st.USER_INTERRUPT ; first_time_here_flag=True
            globs.user_touched_screen_flag=False
            print(" Checking flag indicates that the User has interrrupted loop");                
        if (SerConn.cardID_available):
            timeoutTimer1.reset()
            supervisor_cardID=SerConn.get_cardID()  # get the prox card number of this supervisor swipe  
            Dis.display_message_to_user('Prox Card ID ',1)
            Dis.display_message_to_user(supervisor_cardID,2);
            Dis.display_message_to_user(' ',3)
            Dis.display_message_to_user('As Supervisor',4)
            Dis.display_message_to_user('',5)
            if supervisor_cardID==globs.supervisor_cardID: # if same one as last time, then OK. 
                state= st.CALC_ACCESS_TIME; first_time_here_flag=True;
            else:
                globs.supervisor_cardID=supervisor_cardID  # overwrite supervisor card ID            
                state= st.PROX_SWIPE_FROM_SUPER_OBTAINED ; first_time_here_flag=True;          
        return state,first_time_here_flag     
 #--------------------------------------------------------------              
    if (state== st.PROX_SWIPE_FROM_SUPER_OBTAINED):    
        if (first_time_here_flag==True):
            
            first_time_here_flag=False;
#-------
        (OK,globs.second_swipe_prox_card)=Data.proxcardlookup(globs.supervisor_cardID)  # get info from this  supervisor swipe 
        if OK==False:
                print('finished with an error, let the database guys know')  
                state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
        elif OK==True:
                print('finished with a good result, ',globs.second_swipe_prox_card)
                state= st.GOT_SUPER_ID ;first_time_here_flag=True
        return(state,first_time_here_flag);
 #--------------------------------------------------------------              
    if (state== st.SET_TIMER_FOR_SWITCH_DETECT):    
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(timing_constants.CHECK_SWITCH_STATE_DURATION)
            first_time_here_flag=False
#-------
        else:
            state= st.CHECK_SWITCH_STATE; first_time_here_flag=True 
        return(state,first_time_here_flag);
    #----------------------------------------------------------------        
    if (state== st.CHECK_SWITCH_STATE):   
        if (first_time_here_flag==True):
            if globs.machineTable["uses_estop"]:
                state= st.CALC_ACCESS_TIME; first_time_here_flag=True;
            else:
                print("Doing impedance measurement")
              
                Dis.display_message_to_user('',3)
                Dis.display_message_to_user('Checking',4)
                Dis.display_message_to_user('Power Switch',5)
                 
                first_time_here_flag=False
        else:        
#-------         
            (OK,val) = ACommandProc.complete_impedance_measure()    
            if OK==False:
                print('ERROR in measuring impedance ')
                state=st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=False
            if OK==True:
                print('Impedance measurement is good, value= ',val)
                if val>20000:
                    state= st.CALC_ACCESS_TIME; first_time_here_flag=True;
                else:
                    state= st.IMP_CHECK_FAILED; first_time_here_flag=True;      
        return state,first_time_here_flag             
    #----------------------------------------------------------------        
   
 #----------------------------------------------------------------          
    if (state== st.IMP_CHECK_FAILED):        
        if (first_time_here_flag==True):
            print("Here because of failed impedance test")
            print("Tell user to turn off the power switch")
            Dis.display_message_to_user('Turn Off ',4)
            Dis.display_message_to_user('Power Switch',5)
            timeoutTimer2.set_time(timing_constants.DISPLAY_DELAY)
            
            first_time_here_flag=False
#-------            
        if timeoutTimer1.timed_out():
            state= st.IDLE; first_time_here_flag=True    
        elif  (timeoutTimer2.timed_out()):
            state= st.CHECK_SWITCH_STATE; first_time_here_flag=True 
            
        return state,first_time_here_flag            
   
    #----------------------------------------------------------------          
      
  #----------------------------------------------------------------          
    if (state== st.SERIAL_COMMAND_NOT_RESPONDING):        
        if (first_time_here_flag==True):
            print("Here Because the arduino was sent a command and it did not respond")
            Dis.display_message_to_user('COMMUNICATION ERROR',4)
            timeoutTimer1.set_time(timing_constants.DISPLAY_ERROR_DELAY)
            print("This is just a delay state so the user can read the message")
            print('Send an arduino message to turn the relay off')
            
            first_time_here_flag=False
        OK=ACommandProc.turn_off_device()
        if OK==False:
            print('error in arduino request to turn off device ')
                
        if  timeoutTimer1.timed_out():
            
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
    fake_database=DataBaseV2.DataBase()
    Data=DataBaseQuery.DataBaseQuery(fake_database)
    timeoutTimer1=timeoutTimer.timeoutTimer()
    timeoutTimer2=timeoutTimer.timeoutTimer()
    displayscreen = tk.Tk()
    displayscreen.overrideredirect(True)
    Dis=DisplayStuff.Display(displayscreen);
    timeoutTimer1.set_time(timing_constants.DISPLAY_SOFTWARE_VERSION_TIME)
    while not timeoutTimer1.timed_out():
        pass
    GlobalState= st.IDLE
    print("initial state=",GlobalState)
    flag=True
    while True:
        displayscreen.update_idletasks()
        displayscreen.update()
        SerConn.attempt_to_get_readings();
        #if flag:
            #print("STATE=",GlobalState)
        (s,f)=mainloop(GlobalState,flag);
        
        if f:
            print("newstate=",s)
        (GlobalState,flag) = (s,f)   
        
                
                
