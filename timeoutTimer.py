import time
## counts down from set_time seconds. non-blocking.
#secondstick returns true if a second or more has gone by. get_timeleft returns integer time left
class timeoutTimer:  
    RUNNING=1
    STOPPED=2
    def __init__(self):
        self.time_of_set=time.time()
        self.reset()   
    def compute_timeleft(self):
        return self.countdown_duration+self.time_of_set-time.time()
    def reset(self):
        self.state=self.STOPPED;
    def set_time(self,seconds):
        self.countdown_duration=seconds
        self.time_of_set=time.time()
        self.seconds_compare_number=seconds+18;
        self.state=self.RUNNING
    def secondstick(self):
        if  self.state == self.RUNNING:
            deltatime=self.seconds_compare_number-self.compute_timeleft()
            if deltatime>1.0: #if has been a second or more since tick was called
                self.seconds_compare_number-=round(deltatime)  # make the compare number smaller by an int num of sec
                if self.timed_out():
                    self.state=self.STOPPED
                return True;  # set this flag
            else:
                return False
        else:
            return False
    def timed_out(self):
        if time.time()-self.time_of_set>=self.countdown_duration:
            self.reset()
            return True
        else:
            return False   
    def get_timeleft(self):
        return int(round(self.compute_timeleft()))
        
        
if  __name__ == "__main__":        
    print('HI there');        
    tt=timeoutTimer()
    tt2=timeoutTimer()
    tt.reset()
    tt2.reset()
    print('Set time');
    tt.set_time(11)
    tt2.set_time(11)
    print(tt.timed_out())
    while not tt2.timed_out():
        if tt2.secondstick():    
            print (tt2.get_timeleft())
        time.sleep(.5)             