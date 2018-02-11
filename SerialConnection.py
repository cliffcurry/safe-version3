import serial
import io

import time

class SerialClass():
    #  PUBLIC STUFF-------------------- 
    #  BOOLEAN cardID_available
    #  BOOLEAN commandResponse_available
    #  BOOLEAN alive_available
    #  string getcardID()
    #  string get_command_response()
    #  boolean get_alive()
    #  null  attempt_to_get_readings()
    #  null  close()
    
    def __init__(self):
        #self.ser = serial.Serial('/dev/tty.usbserial', 9600,timeout=1)
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)  ### read() will return bad data if the baudrate is incorrect
        #self.ser.baudrate = 115200
        #self.ser = serial.Serial('COM4', 9600) 
        self.global_partial_line="";
        self.cardID_available=False
        self.commandResponse_available=False
        self.alive_available=False
        self.commandResponse="";
 
    def readln(self):  ### looks for a \n linefeed. removes a single line from the serial buffer. returns that line that it           
        # removed.  if it does not find a line, returns an empty string, and the que  will be empty. If there are 
        # more lines in the que, nothing is done with them until this function is called again.  This function has to 
        #  be called often enough to keep the que from overflowing.  
        #  if the que becomes empty,  saves the partial line  for use later
        #   and returns an empty string. 
        #  also will return an empty string if there is a \n with no other characters on the input. 
        out_line=self.global_partial_line  # each time this routine is entered, initialize the output to the temp store
        while self.ser.in_waiting: # do this over and over again until there is nothing waiting
            c=self.ser.read()   # by defult, reads one byte
            c=str(c.decode("utf-8")) # input is a byte string, different than a string, so must be decoded into a string. 
            if  c == '\n':  # string-string comparison here.  Python alows compare of different types, always will fail on equality. 
                self.global_partial_line="";  # reset temp storag
                return(out_line)  # returns the line, que is not empty, partial line is reset to empty string
            else :
              out_line += c
              self.global_partial_line += c
        # serial buffer is empty here and a newline is not found  
        return ""   
    def parse_line(self,instr):
        if instr[0]=="*":
            #print ("alive")
            self.alive_available=True;
        else:
            par_tuple=instr.partition(" ")  # part before, space, and part after . if no equal, returns str and two empty strings
            if par_tuple[1]  == "" and par_tuple[2] == "":
                print('comment=',instr)
            elif  par_tuple[0]=="+++":
                #print("In SERIAL: response to command")
                ##par_tuple=par_tuple[2].partition(" ") # get part after, now part after is " A 6  534"
                self.commandResponse=par_tuple[2].strip()
                self.commandResponse_available=True  # be sure to put this after the previous line, not before
                
            elif  par_tuple[0] == "===":
                #print( " card read") # part after is "cardsreadnum facility-cardnumber "
                par_tuple=par_tuple[2].partition(" ") # get part after, now part after is "facility-cardnumber"
                #print("After reading this many cards");print(par_tuple[0])
                par_tuple=par_tuple[2].partition("-") # now part after is cardnumber
                #print("facilty number=",par_tuple[0],"card number=", par_tuple[2])
                self.cardID=par_tuple[2].strip();
                self.cardID_available=True;
            else:
                print("In SerialConnection: unusual message received:  ",instr)
            
    def attempt_to_get_readings(self):  #  removes all the lines from the serial buffer. parses those lines, looking for data.
        # if it finds data, then fills the global data array with the data.  is finished when the entire serial buffer is empty. 
        # repeatadly calls readline until the serial buffer is empty. 
        #print("quelength=",working_inque.qsize())
        while self.ser.in_waiting:
                      cd= self.readln()  # remove a single line from the serial buffer. Returns a line or a empty string
                      if cd != "":
                        pt=self.parse_line(cd)  # the tuple that comes back has a TRUE if the line was a full one with data in it. 
                       
    def get_cardID(self):
        if self.cardID_available==True:
            self.cardID_available=False;
            return self.cardID   
        else:
            return NULL
            
    def get_command_response(self):
        if self.commandResponse_available==True:
            self.commandResponse_available=False;
            return self.commandResponse 
        else:
            return NULL            

    def get_alive(self):
        if self.alive_available==True:
            self.alive_available=False;
            return True 
        else:
            return False            
    def send_command(self,instr):
        #print("IN SERIAL: command sent to arduino:"+instr)
        self.ser.write(instr.encode());
        
    
    def send_imp_request(self):
        self.send_command("+++ imp \r\n")
    def relay_mainpowerOFF(self):   
        s=    ("+++ write "+str(MAINPOWER_RELAY_PIN)+" 1 \r\n")
        self.send_command(s); 
    def relay_mainpowerON(self) :       
        self.send_command("+++ write "+str(MAINPOWER_RELAY_PIN)+" 0 \r\n");       
    def close(self):
        return serial.Serial.close(self.ser)
        
if  __name__ == "__main__": 
    print('HI there')     
    s=SerialClass()
    sio = io.TextIOWrapper(io.BufferedRWPair(s.ser,s.ser))
    sio.write(("hello\n"))
    sio.flush() # it is buffering. required to get the data out *now*
    #resp=sio.readline()
    #print(">>"+resp)
    i=0; j=300; k=450;
    while True:
        s.attempt_to_get_readings();
        if s.cardID_available:
            print("cardID=",s.get_cardID())
        if s.commandResponse_available:
            inp=s.get_command_response();
            print("command response=",inp)
        if s.alive_available:
            print("alive=",s.get_alive()) 
        i=i+1;  j=j+1; k=k+1;   
        if i>500:
            i=0
            s.relay_mainpowerOFF()
        if j>500:
            j=0
            s.relay_mainpowerON()
        if k>500:
            k=0
            s.send_imp_request()            
            
        time.sleep(.01)
    s.close()
