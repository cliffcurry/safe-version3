import hardware_const
import timing_constants
import io
import timeoutTimer
import time
import SerialConnection
from enum import Enum

# pins for impedance measurement are hard wired in arduino code. 

#  PUBLIC STUFF-------------------- 
#def turn_off_device() returns True=sucess, False=failure, None=working .Turns off power relay, estop relay, and sense relay
#def turn_on_device()   returns True=sucess, False=failure, None=working .Turns on power relay and estop relay
#def complete_impedance_measure()  returns (state,value) , state= True=sucess, False=failure, None=working. value=impedance in ohms
#-------------------------------------------- functions for more low level stuff

#def turn_off_sense_relay()  returns True=sucess, False=failure, None=working 
#def turn_on_sense_relay()     returns True=sucess, False=failure, None=working
#def read_impedance(): returns True=sucess, False=failure, None=working. impedance in ohms 


# def Arduino_command_response_OK()
 
   
       
   


# command response state defintion.... 
class ComResState(Enum):

        READY=0
        SENT_COMMAND =2
        RECEIVED_RESPONSE =3
        ERROR = 6
   
 # arduino command response dance.... send a command, then  wait to see if the response is correct
 # arduino commands are "read", "write", "analogRead", or "imp"
 # serial_instance is a serial port instantiation from SerialConnection module   
class ArdCommandResponse:
       

 
    def __init__(self,serial_instance):
        self.serport=serial_instance
        # define some variables that are persistent  to the instance 
        self.retval=6   # a number.  value, for reads, is an actual value.   for writes is either 1 or 0 
        self.state=ComResState.READY   # initialize the state
        #print(" intialize state to ",self.state)
        self.timeoutTimer2=timeoutTimer.timeoutTimer()   # create a timout timer to use for serial commands
 
#--------------------------------------------------------------------------------
    # this is an internal state machine function, checking if response is OK
    # returns the next state and the value
    # this is the function called after the command to the arduino has benn initiated (sent) . It checks to see if the appropriate response is received 
    def Arduino_command_response_OK(self):  # returns None= no response , True = good response , False ==bad response
        #--------------    
        # auxillary function for use inside this function, used to check response from a read or from a write.
        # response is capitol W or R, fowwed by arduino pin, followed by a number.
        # returns the number, which is the value of  a read command , or 0 or 1 from a write command
        # if the parsing does not check out, transitions to the error state, else transitions to received response state
        def checkresponse(par_tuple,readwrite,pinstring,onezero='0'): # see if what you received was what you wanted
        #  on input, par_tuple is { string "R" or "W" or "A" , space, rest of the parsed line}
            if par_tuple[0]==readwrite:  # read or write expected and read or write received
                par_tuple=par_tuple[2].partition(" ") # parse rest of line, {should be pin number, space, result of read}  
                if par_tuple[0]==pinstring: #  pin is correct
                    if readwrite=="R" or readwrite=="A": # if the read command returns correct pin, it is OK 
                        state=ComResState.RECEIVED_RESPONSE   # can transition to the ok state 
                        retval=par_tuple[2] # for a read command, value is here. for a write is just '1' or '0' 
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
            return(state,retval)  # end of the aux funtion 
#-----------------------------------------------------------------------------------            
        #print("Arduino command response state is=",self.state)    
#-----------------------------------------------------------------------------------                        
        if self.state == ComResState.READY: # do nothing state
             self.state=ComResState.SENT_COMMAND
             #print("In Ardino command Response OK, state was ready, is now sent command")
             return(None,None)
#---------------------------------------------------------------------------------
        elif self.state == ComResState.SENT_COMMAND:
            self.retval = None
            if self.serport.commandResponse_available:  # checks to see  if a response has come from the serial port
                cresponse=self.serport.get_command_response()
                # print("Received from Arduino:",cresponse)
                self.timeoutTimer2.reset()  # since a response is back, reset the timeout timer
                par_tuple=cresponse.partition(" ")  # parse the command response body
                #  now, we check for the 4 possible sent commands, 'imp', 'write', or 'read'
                if self.command=='imp':   #  if we are waiting for the response of an impedance query..
                    if par_tuple[0]=='imp':  # if the response is correct, for this query 
                        z=float(par_tuple[2]) # the answer in ohms is the number following the "imp" string 
                        self.state=ComResState.RECEIVED_RESPONSE # set state to say "we are done"
                        self.retval=z # return the ohms, too       
                    else:  # query was impedance, but did not receive 'imp' back 
                        print('ERROR,expected "imp" but received ',par_tuple)    # diagnostic message
                        self.state=ComResState.ERROR # error state is next
                        self.retval=None
                elif self.command=='write':   # if we are waiting for the response of a write command
                    (self.state,self.retval)=checkresponse(par_tuple,'W',str(self.pin),str(self.writeval)) # check to see if form is correct
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
        elif self.state == ComResState.RECEIVED_RESPONSE: # means we are finished with a sucessful dance 
            self.state=ComResState.READY
            #print("in ArdCommandResponse, success, return true and state set back to ", self.state)
            return(True,self.retval)
#----------------------------------------------------------------------------   
        elif self.state == ComResState.ERROR:    # means we are finished with an unsucessful dance
            self.state=ComResState.READY; self.retval=None
            print('ERROR, with input command ', self.command," ",self.pin," ",self.writeval)  
            return(False,self.retval)
            
            
    
    #  the following will be called just once, usually, for each command
    #  four different arduino commands "imp",'write',"read","analogRead". creates commands, sends them out
    #  returns immediately. normally returns True, but can return False. (if for example, the arguments are not correct)
    def initiate_arduino_command(self,command,pin='10',writeval='0'):
            # save the input parameters away for use in checking the response 
            self.command=command
            self.pin=pin
            self.writeval=writeval
            
            self.retval = None   # this value is overwritten later, it is superstitius behavior to set it here 
            if self.state== ComResState.READY:
                if command=='imp':
                    s=("+++ imp \r\n")
                    self.serport.send_command(s)
                    timeout=timing_constants.TIME_IT_TAKES_TO_DETECT_SWITCH
                elif command=='write':
                    s=    ("+++ write "+str(pin)+" "+str(writeval)+"\r\n")
                    self.serport.send_command(s); 
                    timeout=timing_constants.ARDUINO_COMMAND_TIMEOUT
                elif command == 'read':
                    s=("+++ read "+ str(pin) + "\r\n")
                    self.serport.send_command(s);  
                    timeout=timing_constants.ARDUINO_COMMAND_TIMEOUT                     
                elif command== 'analogRead':
                    s="+++ analogRead "+ str(pin) + "\r\n"
                    self.serport.send_command(s);  
                    timeout=timing_constants.ARDUINO_COMMAND_TIMEOUT
                else:
                    print("ERROR, in ArdCommandResponse. called initiate_arduino_command with incorrect arguments")
                    self.state=ComResState.ERROR
                    return False  #signifies an error condition 
                self.timeoutTimer2.set_time(timeout) 
                #print(" Arduino command initated=",s); 
                #print(" state was ready, is now set to sent command");
                self.state = ComResState.SENT_COMMAND
                return True # signfies succcessful execution of this function 
            else:
                print("ERROR, called initiate_arduino_command, but we are in state  ", self.state)
                self.state= ComResState.READY
                return False  #signifies an error condition 
  

    class auxState(Enum):

        READY=0
        SENT_COMMAND =2
        RECEIVED_RESPONSE =3
        ERROR = 6
    auxstate=auxState.READY; readval=None
    def read_sequence(self,commandfunction):
        retval=None ; 
        #print(" entering  command dance, auxstate is ",self.auxstate)
        if self.auxstate==self.auxState.READY:  # if in appropriate state
            OK = commandfunction()  # send the command to the arduino
            #print("sent command to arduino")
            if not OK:
                print("error in sending command to arduino, in command dance")
                self.auxstate==self.auxState.ERROR
            else:
                self.auxstate=self.auxState.SENT_COMMAND   
                #print("response was ",OK)
                #print("auxstate set to", self.auxstate)
        elif self.auxstate==self.auxState.SENT_COMMAND: # listen for  result
            (OK,self.readval)=self.Arduino_command_response_OK()
            #print (" in command dance, arduino command response OK returns ",OK)
            if OK==True:
                self.auxstate=self.auxState.RECEIVED_RESPONSE
            elif OK==False:
                print("error in response from arduino to command request") 
                self.auxstate==self.auxState.ERROR
            # third possiblity is OK is none, which means the command is not done yet      
        elif self.auxstate==self.auxState.RECEIVED_RESPONSE: # all is good, the command is complete
            self.auxstate=self.auxState.READY
            retval= True    
        elif self.auxstate==self.auxState.ERROR:  #  there has been a communication error
            print("FATAL ERROR in the command dance")
            time.sleep(50)
            self.auxstate=self.auxState.READY
            retval= False
        return (retval,self.readval)
 
    # returns True-> the command was sent and replied to, False-> there was some error condition, None-> The device is not yet off       
    

    def write_sequence(self,commandfunction):
        (OK,value)=self.read_sequence(commandfunction)
        return OK
    def turn_on_sense_relay(self):    
        done=self.write_sequence(lambda: self.initiate_arduino_command("write",str(hardware_const.SENSE_RELAY_PIN),"0")    )  
        return done
        
    def turn_off_sense_relay(self):    
        done=self.write_sequence(lambda: self.initiate_arduino_command("write",str(hardware_const.SENSE_RELAY_PIN),"1")    )  
        return done 
        
    
        
    def read_impedance(self):    
        (retval,val)=self.read_sequence(lambda: self.initiate_arduino_command('imp','0','0'))
        return (retval,val)         
        
        
        
        
        
        
    # turns off the device by sending three commands to the arduino.        
    class bigState(Enum):
        BEGIN=0
        FIRST_ONE=1
        SECOND_ONE=2
        THIRD_ONE=3
        SUCCESS=4
        ERROR = 6
    mult_state=bigState.BEGIN   
    
    def turn_off_device(self):
        retval=None
        # print("turn off device state=",self.mult_state)
        if self.mult_state==self.bigState.BEGIN:
            self.mult_state=self.bigState.FIRST_ONE
        elif self.mult_state==self.bigState.FIRST_ONE:
            done=self.write_sequence(lambda: self.initiate_arduino_command("write",str(hardware_const.MAINPOWER_RELAY_PIN),"1")     )
            if done==True:
                self.mult_state=self.bigState.SECOND_ONE
            elif done==False:
                self.mult_state=self.bigState.ERROR
        elif self.mult_state==self.bigState.SECOND_ONE:
            done=self.write_sequence(lambda: self.initiate_arduino_command("write",str(hardware_const.ESTOP_RELAY_PIN),"1")   )
            if done==True:
                self.mult_state=self.bigState.THIRD_ONE
            elif done==False:
                self.mult_state=self.bigState.ERROR 
        elif self.mult_state==self.bigState.THIRD_ONE:
            done=self.write_sequence(lambda: self.initiate_arduino_command("write",str(hardware_const.SENSE_RELAY_PIN),"1")   )
            if done==True:
                self.mult_state=self.bigState.SUCCESS
            elif done==False:
                self.mult_state=self.bigState.ERROR 
        elif self.mult_state==self.bigState.SUCCESS:
            retval=True
            self.mult_state=self.bigState.BEGIN
        elif self.mult_state==self.bigState.ERROR:
            retval=False;
            print("ERROR turn device off failed")
            time.sleep(20)
            self.mult_state=self.bigState.BEGIN
        return retval

# turns on the device by sending two commands to the arduino.    

    def turn_on_device(self):
        retval=None
        if self.mult_state==self.bigState.BEGIN:
            self.mult_state=self.bigState.FIRST_ONE
        elif self.mult_state==self.bigState.FIRST_ONE:
            done=self.write_sequence(lambda: self.initiate_arduino_command("write",str(hardware_const.MAINPOWER_RELAY_PIN),"0")     )
            if done==True:
                self.mult_state=self.bigState.SECOND_ONE
            elif done==False:
                self.mult_state=self.bigState.ERROR
        elif self.mult_state==self.bigState.SECOND_ONE:
            done=self.write_sequence(lambda: self.initiate_arduino_command("write",str(hardware_const.ESTOP_RELAY_PIN),"0")   )
            if done==True:
                self.mult_state=self.bigState.SUCCESS
            elif done==False:
                self.mult_state=self.bigState.ERROR 
        elif self.mult_state==self.bigState.SUCCESS:
            retval=True
            self.mult_state=self.bigState.BEGIN
        elif self.mult_state==self.bigState.ERROR:
            retval=False;
            print("ERROR turn device on failed")
            time.sleep(20)
            self.mult_state=self.bigState.BEGIN
        return retval

    class impState(Enum):
        BEGIN=0
        DEVICE_OFF =1
        SENSE_ON=2
        IMP_MEAS=3
        SENSE_OFF=4
        SUCCESS=5
        ERROR = 6
    imp_state=impState.BEGIN ;ohms_measure=None

    def complete_impedance_measure(self):
        retval=None
        # turn off the device 
        if self.imp_state==self.impState.BEGIN:
            OK=self.turn_off_device()
            if OK==False:
                print("in imp meas, Starting the sequence.. but, turnoff of device failed")
                self.imp_state=self.impState.ERROR
            elif OK==True:
                self.imp_state=self.impState.DEVICE_OFF
                print('in impedance, Starting the sequence: device is off')
        elif self.imp_state==self.impState.DEVICE_OFF:
            # turn on the sense relay
            OK=self.turn_on_sense_relay()
            if OK==False:
                print("in imp meas, turn on of sense relay failed")
                self.imp_state=self.impState.ERROR
            elif OK==True:
                self.imp_state=self.impState.IMP_MEAS
                print('in impedance, sense relay  is on')
        elif self.imp_state==self.impState.IMP_MEAS:
            # do the impedance measurement
            (OK,self.ohms_measure)=self.read_impedance()
            if OK==False:
                print("in imp meas, arduino imp command failed")
                self.imp_state=self.impState.ERROR
            elif OK==True:
                self.imp_state=self.impState.SENSE_OFF
                print('in impedance, measurement succeeded')
        elif self.imp_state==self.impState.SENSE_OFF:
            # turn off the sense relay
            OK=self.turn_off_sense_relay()
            if OK==False:
                print("in imp meas, sense relay off failed")
                self.imp_state=self.impState.ERROR
            elif OK==True:
                self.imp_state=self.impState.SUCCESS
                print("in imp meas, sense relay  is off")
        elif self.imp_state==self.impState.SUCCESS:
            print("impedance measurement complete");
            retval=True
            self.imp_state=self.impState.BEGIN
        elif self.imp_state==self.impState.ERROR:
            print("impedance measurement failed");
            time.sleep(10)
            self.imp_state=self.impState.BEGIN
            retval=False           
        return(retval,self.ohms_measure)
            
        
        
        
      









        
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

    s1=1; s2=2; s3=3; s4=4; s5=5;s6=6; s7=7; s8=8; s9=9 ; s10=10; s11=11; s88=88; serr=12; sfinal=99; sxx=76; sxu=46;
    
    mainstate=s1
    while True:     
    
        sport.attempt_to_get_readings(); 
        if sport.cardID_available:
            print("cardID=",sport.get_cardID())
        if sport.alive_available:
            print("alive=",sport.get_alive()) 
           
        if mainstate==s1:
            #print("Test the read sequence") 
            (OK,val)=ACommandProc.read_sequence(lambda: ACommandProc.initiate_arduino_command("read","4","0"))
            if OK:
                 print('reading of pin 4 is   ',val)
                 mainstate=s2
            elif OK==False:
                print('ERROR  with response from the arduino to a read  request, state=',mainstate)
                mainstate=serr
     
        elif mainstate==s2:
            #print("Test the write sequence") 
            OK=ACommandProc.write_sequence(lambda: ACommandProc.initiate_arduino_command("write",str(hardware_const.MAINPOWER_RELAY_PIN),"1")     )
            if OK == True:
                print(' sucess in main relay off')
                mainstate=sxx
            elif OK==False:
                print("ERROR in main relay  TURNING OFF, STATE=",mainstate)
                mainstate=serr
       
        elif mainstate==sxx:
            #print("Test the power off ")
            OK=ACommandProc.turn_off_device()
            if OK == True:
                print(' sucess in turning off device')
                mainstate=s6
            elif OK==False:
                print("ERROR in DEVICE TURNING OFF, STATE=",mainstate)
                mainstate=serr
                
        elif mainstate==s6:
            #print("Test the power on  sequence")
            OK=ACommandProc.turn_on_device()
            if OK == True:
                print(' sucess in turning on device')
                mainstate=s7
            elif OK==False:
                print("ERROR in DEVICE TURNING ON, STATE=",mainstate)
                mainstate=serr
                
        elif mainstate==s7:
            #print("Test the initate command")
            OK=ACommandProc.initiate_arduino_command("analogRead",0)
            if not OK:
                print(' ERROR in call')
                mainstate=serr
            else:
                mainstate=s8
        elif mainstate==s8:
            #print("Test the reply to  command")
            OK,val=ACommandProc.Arduino_command_response_OK()
            if OK:
                 print('read response is ', val)
                 mainstate=s9
            elif OK==False:
                print('ERROR  with response from the arduino to a good request')
                mainstate=serr        
        elif mainstate==s9 :
            #print("Test the sense relay  command")
            OK=ACommandProc.turn_off_sense_relay()
            if OK==False:
                print(' ERROR relay sense off ')
                mainstate=serr
            elif OK==True:
                print ("turned the sense relay off")
                mainstate=s10

        elif mainstate==s10:
           #print("Test the impedance command")
            (OK,impedance)=ACommandProc.complete_impedance_measure()
            if OK==False:
                print(' ERROR impedance measurement ')
                mainstate=serr
            elif OK==True:
                print ("impedance sequence all OK with impedance=",impedance)
                mainstate=s11
        elif mainstate==s11:
         
                mainstate=s88
        elif mainstate==s88: 
           
                mainstate=sfinal   
        elif mainstate==sfinal:
            print("ALL IS GOOD. wait for a few seconds before starting over")
            time.sleep(5)          
        elif mainstate==serr:
            print("ERRORS HERER wait for a few seconds before starting over")
            time.sleep(15)
        time.sleep(.1)
        
    
