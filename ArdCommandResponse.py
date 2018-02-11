import io
import timeoutTimer
import time
import SerialConnection
from enum import Enum

class ComResState(Enum):

        READY=0
  
        SENT_COMMAND =2
        RECEIVED_RESPONSE =3
  
        ERROR = 6
        
        
ARDUINO_COMMAND_TIMEOUT = 20
TIME_IT_TAKES_TO_DETECT_SWITCH =20        
class ArdCommandResponse:
    

    def __init__(self,serial_instance):
        self.serport=serial_instance
        self.retval=6
        self.state=ComResState.READY
        self.timeoutTimer2=timeoutTimer.timeoutTimer()
 

      
  

#--------------------------------------------------------------------------------
    # this is the function called after the command to the arduino has benn initiated (sent) . It checks to see if the appropriate response is received 
    def Arduino_command_response_OK(self):  # returns None= no response , True = good response , False ==bad response
        # auxillary function for use inside this function 
        def checkresponse(par_tuple,readwrite,pinstring,onezero='0'): # see if what you received was what you wanted
            if par_tuple[0]==readwrite:  # read or write expected and read or write received
                par_tuple=par_tuple[2].partition(" ")
                if par_tuple[0]==pinstring: #  pin is correct
                    if readwrite=="R" or "A": # if the read command returns correct pin, it is OK 
                        state=ComResState.RECEIVED_RESPONSE
                        retval=par_tuple[2] # read command, value is here
                    else:  # for write  commands, check the value, too
                        if par_tuple[2]==onezero:  # if it is correct.... 
                            state=ComResState.RECEIVED_RESPONSE
                            retval=None
                        else:
                            state=ComResState.ERROR; retval=None;
                            print('ERROR, command expected ', readwrite," ",pinstring," ",onezero," but received " ,par_tuple)
                            print('last argument (writeval) is incorrect')
                else:
                    state=ComResState.ERROR; retval=None;
                    print('ERROR, command expected ', readwrite," ",pinstring," ",onezero," but received " ,par_tuple)   
                    print(' pin number is incorrect')    
            else:
                state=ComResState.ERROR; retval=None;
                print('ERROR, command expected ', readwrite," ",pinstring," ",onezero," but received " ,par_tuple)
                print('command letter is incorrect')
            return(state,retval)  
            
            
  
#-----------------------------------------------------------------------------------                        
        if self.state == ComResState.READY: # do nothing state
             return(None,None)
#---------------------------------------------------------------------------------
        elif self.state == ComResState.SENT_COMMAND:
            self.retval = None
            if self.serport.commandResponse_available:  # checks to see  if a response has come from the serial port
                cresponse=self.serport.get_command_response()
                # print("Received from Arduino:",cresponse)
                self.timeoutTimer2.reset()  # since a response is back, reset the timeout timer
                par_tuple=cresponse.partition(" ")  # parse the command response body 
                if self.command=='imp':
                    if par_tuple[0]=='imp':
                        z=float(par_tuple[2])
                        self.state=ComResState.RECEIVED_RESPONSE
                        self.retval=z
                        #return(None,self.retval)
                    else:
                        print('ERROR,expected "imp" but received ',par_tuple)    
                        self.state=ComResState.ERROR
                        self.retval=None
                elif self.command=='write':
                    (self.state,self.retval)=checkresponse(par_tuple,'W',str(self.pin),str(self.writeval))
                elif self.command=='read':
                    (self.state,self.retval)=checkresponse(par_tuple,'R',str(self.pin))
                elif self.command=='analogRead':
                    (self.state,self.retval)=checkresponse(par_tuple,'A',str(self.pin)) 
            else:
                if self.timeoutTimer2.timed_out():
                    print('Command Communication timeout from Arduino')
                    self.state=ComResState.ERROR ;self.retval=None
            return(None,self.retval)
#----------------------------------------------------------------------------            
        elif self.state == ComResState.RECEIVED_RESPONSE:
            self.state=ComResState.READY; 
            return(True,self.retval)
#----------------------------------------------------------------------------   
        elif self.state == ComResState.ERROR:
            self.state=ComResState.READY; self.retval=None
            print('ERROR, with input command ', self.command," ",self.pin," ",self.writeval)  
            return(False,self.retval)
            
            
    
    #  the following will be called just once, usually, for each command
    def initiate_arduino_command(self,command,pin='10',writeval='0'):
            # save the input parameters away for use in checking the response 
            self.command=command
            self.pin=pin
            self.writeval=writeval
            
            self.retval = None   # this value is overwritten later, it is superstitius behavior to set it here 
            if self.state== ComResState.READY:
                if command=='imp':
                    self.serport.send_command("+++ imp \r\n")
                    timeout=TIME_IT_TAKES_TO_DETECT_SWITCH
                elif command=='write':
                    s=    ("+++ write "+str(pin)+" "+str(writeval)+"\r\n")
                    self.serport.send_command(s); 
                    timeout=ARDUINO_COMMAND_TIMEOUT
                elif command == 'read':
                    self.serport.send_command("+++ read "+ str(pin) + "\r\n");  
                    timeout=ARDUINO_COMMAND_TIMEOUT                     
                elif command== 'analogRead':
                    self.serport.send_command("+++ analogRead "+ str(pin) + "\r\n");  
                    timeout=ARDUINO_COMMAND_TIMEOUT
                else:
                    print("ERROR, in ArdCommandResponse. called initiate_arduino_command with incorrect arguments")
                    self.state=ComResState.ERROR
                    return False  #signifies an error condition 
                self.timeoutTimer2.set_time(timeout)     
                self.state = ComResState.SENT_COMMAND
                return True # signfies succcessful execution of this function 
            else:
                print("ERROR, called initiate_arduino_command, but we are nin state  ", self.state)
                self.state= ComResState.READY
                return False  #signifies an error condition 
                
    MAINPOWER_RELAY_PIN=10        
     
    def send_imp_request(self):
        OK =self.initiate_arduino_command('imp','0','0')
        return OK
    def send_relay_mainpowerOFF(self):   
        OK = self.initiate_arduino_command("write",str(self.MAINPOWER_RELAY_PIN),"1")
        return OK
    def send_relay_mainpowerON(self) :       
        OK=self.initiate_arduino_command("write",str(self.MAINPOWER_RELAY_PIN),"0")          
        return OK    
            
            
            

if  __name__ == "__main__": 
    print('HI there')     
    # define the serial port 
    sport=SerialConnection.SerialClass()
    sio = io.TextIOWrapper(io.BufferedRWPair(sport.ser,sport.ser))
    sio.write(("hello\n"))
    sio.flush() # it is buffering. required to get the data out *now*
    # define the command processor
    ACommandProc=ArdCommandResponse(sport)
    stophere=True
    while stophere:    
        sport.attempt_to_get_readings(); 
        if sport.cardID_available:
            print("cardID=",sport.get_cardID())
        if sport.alive_available:
            print("alive=",sport.get_alive()) 
            stophere=False
    print('Arduino is alive ')   
    i=0; j=300; k=450;
    s1=1; s2=2; s3=3; s4=4; s5=5;s6=6; s7=7; s8=8; s9=9
    
    mainstate=s1
    while True:     
    
        sport.attempt_to_get_readings(); 
        if sport.cardID_available:
            print("cardID=",sport.get_cardID())
        if sport.alive_available:
            print("alive=",sport.get_alive()) 
            
        if mainstate==s1:
            OK=ACommandProc.send_imp_request()
            if not OK:
                print(' ERROR in call')
            else:
                mainstate=s2
        elif mainstate==s2:
            OK,val=ACommandProc.Arduino_command_response_OK()
            if OK:
                 print('imp response is  ',val)
                 mainstate=s3
            elif OK==False:
                print('some kind of error with communication')
                
        elif mainstate==s3:
            OK=ACommandProc.send_relay_mainpowerON()
            if not OK:
                print(' ERROR in call')
            else:
                mainstate=s4
        elif mainstate==s4:
            OK,val=ACommandProc.Arduino_command_response_OK()
            if OK:
                 print('write response is OK in state ',mainstate)
                 mainstate=s5
            elif OK==False:
                print('some kind of error with communication')
                
        elif mainstate==s5:
            OK=ACommandProc.send_relay_mainpowerOFF()
            if not OK:
                print(' ERROR in call')
            else:
                mainstate=s6
        elif mainstate==s6:
            OK,val=ACommandProc.Arduino_command_response_OK()
            if OK:
                 print('write response is OK in state ',mainstate)
                 mainstate=s7
            elif OK==False:
                print('some kind of error with communication')
        elif mainstate==s7:
            OK=ACommandProc.initiate_arduino_command("analogRead",0)
            if not OK:
                print(' ERROR in call')
            else:
                mainstate=s8
        elif mainstate==s8:
            OK,val=ACommandProc.Arduino_command_response_OK()
            if OK:
                 print('read response is ', val)
                 mainstate=s9
            elif OK==False:
                print('some kind of error with communication')        
        elif mainstate==s9 :
            mainstate=s1
           
           
        time.sleep(.2)
        
    
