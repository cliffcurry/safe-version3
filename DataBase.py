# program that simulates a real data base 

import timeoutTimer

class DataBase():
   
    def __init__(self):
        self.delay_expired=False
        self.tmer=timeoutTimer.timeoutTimer()
        
    def query(self,cardID,machineID):
        self.cardID=cardID  #save card Id
        self.machineID=machineID    #save machine id

        self.tmer.set_time(4)   # sets the delay between a request is sent and this program return the result 
        
    def query_result_available(self):
        if not self.tmer.timed_out():
            return False
        else:
            self.tmer.reset();
            return True
        
    def get_database_response(self):
 # (user_name,user_access_result,reason,user_supervisor,user_time_of_access)
        if self.cardID == "0080486":
            name="Clifford Curry"
            access_result="IS_SUPERVISOR"
            reason=None
            supervisor_name="Brian Snider"
            time_of_access=30
        elif self.cardID == "0158076":
            name="Brian Snider"
            access_result="IS_SUPERVISOR"
            reason="Not Trusted"
            supervisor_name="Fred Flintstone"
            time_of_access=47
        elif self.cardID == "0090001":
            name="John Kostman"
            access_result="SUPERVISOR"
            reason=None
            supervisor_name="Clifford Curry"
            time_of_access=75
        else: 
            name=None
            access_result=None
            reason=None
            supervisor_name=None
            time_of_access=None

        return (name,access_result,reason,supervisor_name,time_of_access)
            
    
     
        
if  __name__ == "__main__": 
    print('HI there')   
    maintimer=timeoutTimer.timeoutTimer()
    d=DataBase()
    maintimer.set_time(70)
    d.query("0080486","007")
    while not d.query_result_available(): 
        pass
    print(d.get_database_response())
    d.query("0097654","003")
    while not d.query_result_available(): 
        pass
    print(d.get_database_response())
    d.query("0080487","005")
    while not d.query_result_available(): 
        pass
    print(d.get_database_response())
    if maintimer.timed_out():
        print("timeout")
        
       