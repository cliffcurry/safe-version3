import timeoutTimer
import SerialConnection
import DataBase
import DisplayStuff
import tkinter as tk
global globs.machineID
globs.machineID=12345
DATABASE_QUERY_TIMEOUT=50
timing_constants.DISPLAY_DELAY=3

globs.user_name="John Doe"
globs.user_time_of_access=30
globs.user_supervisor="John Kostman"
def minutes_display(seconds):
    min=seconds//60
    sec=seconds-min*60
    return str(min)+":"+str(sec)
    
def mainloop(state,first_time_here_flag):
    global globs.user_name
    global globs.user_time_of_access
    
    if (state==IDLE):
        if (first_time_here_flag==True):
            SerConn.cardID_avalable=False; 
            Dis.display_message_to_user('Swipe card for Access',1)
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            first_time_here_flag=False;
        if (SerConn.cardID_available):
            cardID=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID',1);
            Dis.display_message_to_user(cardID,2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            Data.query(cardID,globs.machineID)
            state=WAIT_FOR_FIRST_DATABASE_RESPONSE ; first_time_here_flag=True;
        return (state,first_time_here_flag) 
    #---------------------------------------------------------
    if (state==WAIT_FOR_FIRST_DATABASE_RESPONSE):
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(DATABASE_QUERY_TIMEOUT)
            first_time_here_flag=False;
        if (Data.query_result_available()):
            timeoutTimer1.reset()
            (globs.user_name,access_result,reason,globs.user_supervisor,globs.user_time_of_access)=Data.get_database_response()
            Dis.display_message_to_user(globs.user_name,1);
            if (access_result=='DENIED'):
                Dis.display_message_to_user('ACCESS DENIED',2)
                if (reason):
                    Dis.display_message_to_user(reason,3)
                else:
                    Dis.display_message_to_user('reason not available',3)
                state=WAIT_TO_RESET;      
            elif (access_result=='SUPERVISOR'):
                  state=SUPERVISOR_NEEDED_NOTIFY ;  first_time_here_flag=True   
            else:#(access_result=OK)
                  state=TIMEING_ACCESS ;first_time_here_flag=True
        return (state,first_time_here_flag)           
    #--------------------------------------------------------------  

    
    if (state==SUPERVISOR_NEEDED_NOTIFY):    
        if (first_time_here_flag==True):
            Dis.display_message_to_user('Trouble Connecting to Database',1);
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            first_time_here_flag=False;
        state=WAIT_TO_RESET; first_time_here_flag=True;
        return state,first_time_here_flag 

    #--------------------------------------------------------------    
    if (state==DATABASE_QUERY_TIMED_OUT):    
        if (first_time_here_flag==True):
            Dis.display_message_to_user('Trouble Connecting to Database',1);
            Dis.display_message_to_user('',2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            first_time_here_flag=False;
        state=WAIT_TO_RESET; first_time_here_flag=True;
        return state,first_time_here_flag 
#--------------------------------------------------------------              
    if (state==WAIT_TO_RESET):    
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(timing_constants.DISPLAY_DELAY)
            first_time_here_flag=False;
        if (timeoutTimer1.timed_out()):
            state=IDLE; first_time_here_flag=True;
        return state,first_time_here_flag 
    #--------------------------------------------------------------              
    if (state==SUPERVISOR_NEEDED):    
        if (first_time_here_flag==True):
            timeoutTimer1.set_time(DATABASE_QUERY_TIMEOUT)
            first_time_here_flag=False;
        if (response_from_database_available()):
            database_response=get_database_response()
            timeoutTimer1.reset
            (self.supervisor_name,access_result,reason,supervisor_name)=Data.get_database_response()
            Dis.display_message_to_user(name)
            if (access_result==DENIED):
                Dis.display_message_to_user('ACCESS DENIED',2)
                if (reason):
                    Dis.display_message_to_user(reason,3)
                else:
                    Dis.display_message_to_user('reason not available',3)
                state=WAIT_TO_RESET; first_time_here_flag=True;    
            else:#(access_result=OK)
                  state=TIMEING_ACCESS; first_time_here_flag=True;                  
        if (timeoutTimer1.timed_out()):
            state=WAIT_TO_RESET; first_time_here_flag=True
        return state,first_time_here_flag 
    #----------------------------------------------------------------        
    if (state==TIMEING_ACCESS):        
        if (first_time_here_flag==True):
            Dis.display_message_to_user(globs.user_name,1)
            Dis.display_message_to_user('Has access for',2)
            timeoutTimer1.set_time(globs.user_time_of_access);
            Dis.display_message_to_user(minutes_display(globs.user_time_of_access),3);
            Dis.display_message_to_user('Minutes',4)
            first_time_here_flag=False
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user(minutes_display(timeoutTimer1.get_timeleft()),3)
        if (timeoutTimer1.get_timeleft()<=globs.user_time_of_access//5):
                state=EXTEND_TIME_PROMPT; first_time_here_flag=True
        if (timeoutTimer1.timed_out()):
            state=IDLE; first_time_here_flag=True;        
        return state,first_time_here_flag 
    #----------------------------------------------------------------        
    if (state==EXTEND_TIME_PROMPT):        
        if (first_time_here_flag==True):
            SerConn.cardID_avalable=False; 
            Dis.display_message_to_user('You can now extend access ',5)
            timeoutTimer1.set_time(globs.user_time_of_access//5)
            first_time_here_flag=False
        if (timeoutTimer1.secondstick()):
            Dis.display_message_to_user(minutes_display(timeoutTimer1.get_timeleft()),3)
        if (SerConn.cardID_available):
            cardID=SerConn.get_cardID()
            Dis.display_message_to_user('Prox Card ID',1);
            Dis.display_message_to_user(cardID,2)
            Dis.display_message_to_user('',3)
            Dis.display_message_to_user('',4)
            Dis.display_message_to_user('',5)
            Data.query(cardID,globs.machineID)
            state=WAIT_FOR_FIRST_DATABASE_RESPONSE ; first_time_here_flag=True;
        if (timeoutTimer1.timed_out()):
            state=IDLE; first_time_here_flag=True;
        return state,first_time_here_flag 
    #----------------------------------------------------------------        
    if (state==CHECK_FOR_CLOSED_POWER_SWITCH):        
        if (first_time_here_flag==True):
            Dis.display_message_to_user('Is the Machine on?',4)
            timeoutTimer1.set_time(TIME_IT_TAKES_TO_DETECT_SWITCH);
            first_time_here_flag=False
        relay.mainpowerOFF()
        if switchroutine.determined_closed():
            Dis.display_message_to_user('Machine power switch on: Turn OFF',4)
            state=CHECK_FOR_CLOSED_POWER_SWITCH
        if switchroutne.determined_open():
            Dis.display_message_to_user('Power switch off',4)
            state==TIMEING_ACCESS ; first_time_here_flag=True
        if timeoutTimer1.timed_out():
            Dis.display_message_to_user('INTERNAL ERROR with power switch detection',4)
            state=WAIT_TO_RESET ;first_time_here_flag=True
        return state,first_time_here_flag 
                         
                
if  __name__ == "__main__":     
    IDLE=0   # ready for the card to be swiped
    WAIT_FOR_FIRST_DATABASE_RESPONSE=1   # database has been quiried, waiting for it to respond
    WAIT_TO_RESET=2 
    DATABASE_QUERY_TIMED_OUT=3
    SUPERVISOR_NEEDED=4
    TIMEING_ACCESS=5
    EXTEND_TIME_PROMPT=6
    CHECK_FOR_CLOSED_POWER_SWITCH=7
    #
    SerConn=SerialConnection.SerialClass()
    Data=DataBase.DataBase()
    timeoutTimer1=timeoutTimer.timeoutTimer()
    timeoutTimer2=timeoutTimer.timeoutTimer()
    displayscreen = tk.Tk()
    displayscreen.overrideredirect(True)
    Dis=DisplayStuff.Display(displayscreen);
    state=IDLE
    flag=True
    while True:
        SerConn.attempt_to_get_readings();
        if flag:
            print("STATE=",state)
        (s,f)=mainloop(state,flag);
        if f:
            print("newstate=",s);
        (state,flag) = (s,f)   
        
                
                