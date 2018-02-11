import timeoutTimer
import SerialConnection
import DataBase
import DisplayStuff
import tkinter as tk

from enum import Enum
class st(Enum):
    IDLE= 11 #  #0   # ready for the card to be swiped
    IDLEb= 12 #  #0   # ready for the card to be swiped
    WAIT_FOR_FIRST_DATABASE_RESPONSE= 13 #  #1   # database has been quiried, waiting for it to respond
    WAIT_TO_RESET= 14 #  #2 
    DATABASE_QUERY_TIMED_OUT= 15 #  #3
    SUPERVISOR_NEEDED_CARD= 16 #  #4
    SUPERVISOR_NEEDED_WAIT_FOR_DATA= 17 #  #8
    TIMEING_ACCESS= 18 #  #5
    EXTEND_TIME_PROMPT= 19 #  #6
    CHECK_FOR_CLOSED_POWER_SWITCHa= 100 #  #7
    CHECK_FOR_CLOSED_POWER_SWITCHb= 101 #  #9
    POWER_SWITCH_CLOSED= 102 #  #10
    SERIAL_COMMAND_NOT_RESPONDING= 103 #  #12
    POWER_SWITCH_PREAMBLE= 104 #  #11
    EXTENDED_ACCESS_SWIPE= 105 # 
    SUPERVISOR_NEEDED_EXTENDED= 106 # 
    SUPERVISOR_NEEDED_WAIT_FOR_DATA_EXTENDED= 107 # 
    WRONG_ID_SWIPE= 108 # 
    EXTENDED_ATIME_PROMPT= 109 # 

DATABASE_QUERY_TIMEOUT=50
DISPLAY_DELAY=5
WAIT_FOR_SUPERVISOR_TIME=20
TIME_IT_TAKES_TO_DETECT_SWITCH=60
SERIAL_TIMEOUT_TIME=10

machineID=12345
user_name="John Doe"
user_time_of_access=30
user_supervisor="John Kostman"
user_cardID="0089765"
user_access_result='OK'

def minutes_display(seconds):
    min=seconds//60
    sec=seconds-min*60
    return str(min)+":"+str(sec)
    
def mainloop(state,first_time_here_flag):
    global user_name
    global user_time_of_access
    global user_supervisor
    global user_access_result
    global user_cardID
    global machineID
    if (state== st.IDLE):
        if (first_time_here_flag==True):
            SerConn.cardID_avalable=False; 
            Dis.display_message_to_user('Swipe card for Access',1)
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            print("turn the power switch off")
            timeoutTimer1.set_time(SERIAL_TIMEOUT_TIME)
            print("Sending Arduino message to turn off relay")
            SerConn.relay_mainpowerOFF()
            first_time_here_flag=False
        if SerConn.commandResponse_available: # look for relay off response
            cresponse=SerConn.get_command_response()
            print("Relay off response from Arduino is= ",cresponse)
            state= st.IDLEb; first_time_here_flag=True;
        if  (timeoutTimer1.timed_out()):   
            state= st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=True;
        return state,first_time_here_flag  
    #---------------------------------------------------------
    if (state== st.IDLEb):
        if (first_time_here_flag==True):
            SerConn.cardID_avalable=False; 
            Dis.display_message_to_user('Swipe card for Access',1)
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            first_time_here_flag=False;
        if (SerConn.cardID_available):
            user_cardID=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID',1);
            Dis.display_message_to_user(user_cardID,2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            Data.query(user_cardID,machineID)
            state= st.WAIT_FOR_FIRST_DATABASE_RESPONSE ; first_time_here_flag=True;
        return (state,first_time_here_flag) 
    #---------------------------------------------------------
    if (state== st.WAIT_FOR_FIRST_DATABASE_RESPONSE):
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(DATABASE_QUERY_TIMEOUT)
            first_time_here_flag=False;
        if (Data.query_result_available()):
            timeoutTimer1.reset()
            (user_name,user_access_result,reason,user_supervisor,user_time_of_access)=Data.get_database_response()
            if (user_name==None):
                Dis.display_message_to_user('ACCESS DENIED',3)
                Dis.display_message_to_user('because of',4)
                Dis.display_message_to_user('Unrecognized ID',5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True  
                return (state,first_time_here_flag)  
            else:
                Dis.display_message_to_user(user_name,1);
            if (user_access_result=='DENIED'):
                Dis.display_message_to_user('ACCESS DENIED',3)
                if (reason):
                    Dis.display_message_to_user(reason,4)
                else:
                    Dis.display_message_to_user('no reason ',4)
                state= st.WAIT_TO_RESET;   first_time_here_flag=True 
            elif (user_access_result=='SUPERVISOR'):
                  state= st.SUPERVISOR_NEEDED_CARD ;  first_time_here_flag=True   
            else:#(user_access_result=OK)
                  state= st.CHECK_FOR_CLOSED_POWER_SWITCHa ;first_time_here_flag=True
        if (timeoutTimer1.timed_out()):
            state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True
        return (state,first_time_here_flag)           
    #--------------------------------------------------------------  

    
    if (state== st.SUPERVISOR_NEEDED_CARD):    
        if (first_time_here_flag==True):
            SerConn.cardID_avalable=False
            Dis.display_message_to_user('Supervisor req.',2);
            if user_supervisor==None:
                 user_supervisor='the supervisor'
            Dis.display_message_to_user('Ask '+user_supervisor,3)
            Dis.display_message_to_user('to swipe card',4)
            timeoutTimer1.set_time(WAIT_FOR_SUPERVISOR_TIME)
            first_time_here_flag=False;   
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user("Waiting for " + minutes_display(timeoutTimer1.get_timeleft()),5)
        if (timeoutTimer1.timed_out()):
           state= st.IDLE ; first_time_here_flag=True;          
        if (SerConn.cardID_available):
            timeoutTimer1.reset()
            cardID=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID ',1)
            Dis.display_message_to_user(cardID,2)
            Dis.display_message_to_user('as supervisor',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            Data.query(cardID,machineID)
            state= st.SUPERVISOR_NEEDED_WAIT_FOR_DATA ; first_time_here_flag=True;          
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
            timeoutTimer1.set_time(DISPLAY_DELAY)
            first_time_here_flag=False;
        if (timeoutTimer1.timed_out()):
            state= st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag 
    #--------------------------------------------------------------              
    if (state== st.SUPERVISOR_NEEDED_WAIT_FOR_DATA):    
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(DATABASE_QUERY_TIMEOUT)
            first_time_here_flag=False;
        if (Data.query_result_available()):
            timeoutTimer1.reset()
            (name,access_result,reason,supervisor,time_of_access)=Data.get_database_response()
            if (access_result=='IS_SUPERVISOR'):
                state= st.CHECK_FOR_CLOSED_POWER_SWITCHa ;first_time_here_flag=True
            else:
                Dis.display_message_to_user('Is not an',4)
                Dis.display_message_to_user(' authorized ID',5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True;                 
        if (timeoutTimer1.timed_out()):
            state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True          
        return state,first_time_here_flag 
    #----------------------------------------------------------------        
    if (state== st.TIMEING_ACCESS):        
        if (first_time_here_flag==True):
            Dis.display_message_to_user(user_name,1)
            Dis.display_message_to_user('Has access for',2)
            timeoutTimer1.set_time(user_time_of_access);
            Dis.display_message_to_user(minutes_display(user_time_of_access),3);
            Dis.display_message_to_user('Minutes',4)
            Dis.display_message_to_user('',5)
            SerConn.relay_mainpowerON();
            first_time_here_flag=False
        if SerConn.commandResponse_available:
            cresponse=SerConn.get_command_response()   
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user(minutes_display(timeoutTimer1.get_timeleft()),3)
        if (timeoutTimer1.get_timeleft()<=user_time_of_access//5):
                state= st.EXTEND_TIME_PROMPT; first_time_here_flag=True
        if (timeoutTimer1.timed_out()):
            state= st.IDLE; first_time_here_flag=True;        
        return state,first_time_here_flag 
    #----------------------------------------------------------------        
    if (state== st.EXTEND_TIME_PROMPT):        
        if (first_time_here_flag==True):
            SerConn.cardID_avalable=False
            Dis.display_message_to_user('Swipe to extend access ',5)
            timeoutTimer1.set_time(user_time_of_access//5)
            first_time_here_flag=False
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user(minutes_display(timeoutTimer1.get_timeleft()),3)
        if (SerConn.cardID_available):
            state= st.EXTENDED_ACCESS_SWIPE ; first_time_here_flag=True;
        if (timeoutTimer1.timed_out()):
            state= st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag 
 #----------------------------------------------------------------        
    if (state== st.EXTENDED_ACCESS_SWIPE):        
        if  first_time_here_flag==True:
            cardID=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID',1);
            Dis.display_message_to_user(cardID,2)
            if cardID != user_cardID:
                state=st.WRONG_ID_SWIPE;first_time_here_flag=True;
            else:
                if user_access_result=="SUPERVISOR":
                    state=st.SUPERVISOR_NEEDED_EXTENDED;first_time_here_flag=True;  
                else:  ## user does not need supervisor here 
                    state=st.TIMEING_ACCESS; first_time_here_flag=True;   
        return state,first_time_here_flag     
 #----------------------------------------------------------------        
    if (state== st.WRONG_ID_SWIPE):        
        if (first_time_here_flag==True):
            Dis.display_message_to_user('Is not the ID ',3)
            Dis.display_message_to_user('used previously.',4)
            Dis.display_message_to_user('Access Denied',5)
            timeoutTimer1.set_time(DISPLAY_DELAY)
            first_time_here_flag=False;        
        if (timeoutTimer1.timed_out()):
            state= st.IDLE; first_time_here_flag=True;
        return state,first_time_here_flag           

#---------------------------------------------------------
    if (state== st.SUPERVISOR_NEEDED_EXTENDED):    
        if (first_time_here_flag==True):
            SerConn.cardID_avalable=False
            Dis.display_message_to_user('OK, Supervisor required',2);
            Dis.display_message_to_user('Ask '+user_supervisor,3)
            Dis.display_message_to_user('to swipe card',4)
            timeoutTimer1.set_time(WAIT_FOR_SUPERVISOR_TIME)
            first_time_here_flag=False;   
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user("Waiting for " + minutes_display(timeoutTimer1.get_timeleft()),5)
        if (timeoutTimer1.timed_out()):
           state= st.IDLE ; first_time_here_flag=True;          
        if (SerConn.cardID_available):
            timeoutTimer1.reset()
            cardID=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID ',1)
            Dis.display_message_to_user(cardID,2);
            Dis.display_message_to_user('',5)
            Data.query(cardID,machineID)
            state= st.SUPERVISOR_NEEDED_WAIT_FOR_DATA_EXTENDED ; first_time_here_flag=True;          
        return state,first_time_here_flag     
  #--------------------------------------------------------------              
    if (state== st.SUPERVISOR_NEEDED_WAIT_FOR_DATA_EXTENDED):    
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(DATABASE_QUERY_TIMEOUT)
            first_time_here_flag=False;
        if (Data.query_result_available()):
            timeoutTimer1.reset()
            (name,access_result,reason,supervisor,time_of_access)=Data.get_database_response()
            if (access_result=='IS_SUPERVISOR'):
                state= st.TIMEING_ACCESS ;first_time_here_flag=True
            else:
                Dis.display_message_to_user('Is not an authorized ID',5)
                state= st.WAIT_TO_RESET; first_time_here_flag=True;                 
        if (timeoutTimer1.timed_out()):
            state= st.DATABASE_QUERY_TIMED_OUT; first_time_here_flag=True          
        return state,first_time_here_flag    
    #----------------------------------------------------------------        
    if (state== st.CHECK_FOR_CLOSED_POWER_SWITCHa):   
        
        if (first_time_here_flag==True):
            print("First state for checking the power switch position")
            print("Tell the user I am checking")
            Dis.display_message_to_user('Checking',4)
            Dis.display_message_to_user('Power Switch',5)
            timeoutTimer1.set_time(DISPLAY_DELAY)
            print("Sending Arduino message to turn off relay")
            SerConn.relay_mainpowerOFF()
            first_time_here_flag=False
        if SerConn.commandResponse_available: # look for relay off response
            cresponse=SerConn.get_command_response()
            print("Relay off response from Arduino is= ",cresponse)
            state= st.CHECK_FOR_CLOSED_POWER_SWITCHb; first_time_here_flag=True;
        if  (timeoutTimer1.timed_out()):   
            state= st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=True;
        return state,first_time_here_flag             
    #----------------------------------------------------------------        
    if (state== st.CHECK_FOR_CLOSED_POWER_SWITCHb):        
        if (first_time_here_flag==True):
            print("Here because power relay is succesfully off")
            print("Continue to Tell the user I am checking")
            Dis.display_message_to_user('Checking',4)
            Dis.display_message_to_user('Power Switch',5)
            timeoutTimer1.set_time(TIME_IT_TAKES_TO_DETECT_SWITCH);
            SerConn.send_imp_request() 
            print("Sending impedance request to Arduino")
            first_time_here_flag=False
        if SerConn.commandResponse_available: # look for impedance response
            cresponse=SerConn.get_command_response()
            print("impedance  response here ",cresponse)
            par_tuple=cresponse.partition(" ");
            if par_tuple[0]=='imp':
                z=float(par_tuple[2]);
                if z>20000:
                    state= st.TIMEING_ACCESS; first_time_here_flag=True;
                else:
                    state= st.POWER_SWITCH_PREAMBLE; first_time_here_flag=True;
        if  timeoutTimer1.timed_out():
            print("TIMEOUT, impedance response from Arduino not received")
            state= st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=True;
       
        return state,first_time_here_flag 
 #----------------------------------------------------------------          
    if (state== st.POWER_SWITCH_PREAMBLE):        
        if (first_time_here_flag==True):
            print("Here because of failed impedance test")
            print("Tell user to turn off the power switch")
            Dis.display_message_to_user('Turn Off ',4)
            Dis.display_message_to_user('Power Switch',5)
            timeoutTimer1.set_time(DISPLAY_DELAY)
            SerConn.relay_mainpowerOFF()
            print("Send Arduino command to turn off relay")
            first_time_here_flag=False
        if SerConn.commandResponse_available:
            cresponse=SerConn.get_command_response()
            print("Received from Arduino:",cresponse)
            state= st.POWER_SWITCH_CLOSED; first_time_here_flag=True;
        if  (timeoutTimer1.timed_out()):
            state= st.SERIAL_COMMAND_NOT_RESPONDING; first_time_here_flag=True                      
        return state,first_time_here_flag            
   
    #----------------------------------------------------------------          
    if (state== st.POWER_SWITCH_CLOSED):        
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(.5)
            print("Here because Arduino responded to relayOFF correctly")
            print("Just a delay state")
            first_time_here_flag=False
        if  timeoutTimer1.timed_out():
            state= st.CHECK_FOR_CLOSED_POWER_SWITCHa; first_time_here_flag=True                       
        return state,first_time_here_flag                 
  #----------------------------------------------------------------          
    if (state== st.SERIAL_COMMAND_NOT_RESPONDING):        
        if (first_time_here_flag==True):
            print("Here Because the arduino was sent a command and it did not respond")
            Dis.display_message_to_user('COMMUNICATION ERROR',4)
            timeoutTimer1.set_time(DISPLAY_DELAY)
            print("This is just a delay state so the user can read the message")
            SerConn.relay_mainpowerOFF()
            first_time_here_flag=False
        if  timeoutTimer1.timed_out():
            x=timeoutTimer1.get_timeleft()
            state= st.IDLE; first_time_here_flag=True                    
        return state,first_time_here_flag    



        
if  __name__ == "__main__":     
 
    SerConn=SerialConnection.SerialClass()
    Data=DataBase.DataBase()
    timeoutTimer1=timeoutTimer.timeoutTimer()
    timeoutTimer2=timeoutTimer.timeoutTimer()
    displayscreen = tk.Tk()
    displayscreen.overrideredirect(True)
    Dis=DisplayStuff.Display(displayscreen);
    timeoutTimer1.set_time(5)
    while not timeoutTimer1.timed_out():
        pass
    state= st.IDLE
    print("initial state=",state)
    flag=True
    while True:
        SerConn.attempt_to_get_readings();
        #if flag:
            #print("STATE=",state)
        (s,f)=mainloop(state,flag);
        if f:
            print("newstate=",s);
        (state,flag) = (s,f)   
        
                
                
