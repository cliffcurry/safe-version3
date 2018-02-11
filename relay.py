    
COMMAND_RESPONSE_TIME=0.5
class relay:
    def write(pin,val): # pin and val are strings
        if (first_time_here_flag==True):
            SerConn.commandResponse_available=False
            SerConn.send_command('write ' + pin + ' ' + val)
            timoutTimer2.set_timeout(COMMAND_RESPONSE_TIME)
            first_time_here_flag = False
        if SerConn.commandResponse_available:
            timeoutTimer2.reset
            instr=SerConn.get_command_response()
            parts=instr.partition(" ")
            parts=parts.partition(" ") 
            arduinopin=parts[0]
            parts=parts.partition(" ")
            value=parts[0]
            if arduinopin==pin and value==val:
                return True
            else:
                return False
        if timoutTimer2.timed_out():    
            return False

     def aread(pin): # pin is string, returns a string
        if (first_time_here_flag==True):
            SerConn.commandResponse_available=False
            SerConn.send_command('analogRead ' + pin )
            timoutTimer2.set_timeout(COMMAND_RESPONSE_TIME)
            first_time_here_flag = False
        if SerConn.commandResponse_available:
            timeoutTimer2.reset
            instr=SerConn.get_command_response()
            parts=instr.partition(" ")
            parts=parts.partition(" ") 
            arduinopin=parts[0]
            parts=parts.partition(" ")
            value=parts[0]
            if arduinopin==pin:
                return (True,value)
            else:
                return (False, None)
        if timoutTimer2.timed_out():    
            return (False, None)
i=0    
s=STATE1    
while i<40:  
    if s==STATE1:  # drive side 1 high
        (done)=write(1,1);
        if done:
            s=STATE1b
    if s==STATE1b:   # drive side 2 low
        (done)=write(2,0);
        if done:
            s=STATE2
    if s==STATE2:    # measure the voltage of side 1
        (stat,volts)=aread (0)
        if stat==True:        
            pluss1volts=pluss1volts+volts  # accumulate voltage in side1volts
            s=STATE2b
    if s==STATE2b:    # measure the voltage of side 2
        (stat,volts)=aread (1)
        if stat==True:        
            pluss2volts=pluss2volts+volts # accumulate voltage in side2volts
            s=STATE3            
    if s==STATE3:   # drive side 1 low
        (done)=write(1,0);
        if done:
            s=STATE3b
    if s==STATE3b:    # drive side 2 high
        (done)=write(2,1);
        if done:
            s=STATE4
    if s==STATE4: # measure the voltage of side 1
        (stat,volts)=aread (0);
        if stat==True:        
            minuss1volts=minuss1volts+volts # accumulate voltage in side1volts
            s=STATE4b            
    if s==STATE4b:    # measure the voltage of side 2
        (stat,volts)=aread (1)
        if stat==True:        
            minuss2volts=minuss2volts+volts # accumulate voltage in side2volts
            s=STATE5
    i=i+1            
plusvolts=pluss1volts-pluss2volts
minusvolts=minuss1volts-minuss2volts    