
# program that timeouts the database queries
import timeoutTimer
import DataBase
from enum import Enum
class stEnum(Enum):

        READY=0
        SENT_REQUEST =2
        DONE = 5
        ERROR = 6
        

class DataBaseQuery:  #pass it the database class, which has query, avalible functions built into it. 
 
    
    def __init__(self,db):
        self.database=db
        self.tmer=timeoutTimer.timeoutTimer()
        self.dbst=stEnum.READY
        self.request_cardID="0056793"
        self.request_machineID="45677"
        self.val=None
        
    def query(self,cardID,machineID):
        self.database.query(cardID,machineID)  # send a query out to the database
       
    def query_result_available(self):
        return self.database.query_result_available()
        
    def get_database_response(self):
        (name,access_result,reason,supervisor_name,time_of_access)=self.database.get_database_response();
        return (name,access_result,reason,supervisor_name,time_of_access)
    
    def db_req_response(self):
    
        if  self.dbst == stEnum.READY:    # beginning of the state machine
            return None,None
        elif    self.dbst == stEnum.SENT_REQUEST: # second stage of state machine
            if self.tmer.timed_out():               # if timed out, there has been no response
                print('In db_req_response, timeout, (set to ',self.DATABASE_TIMEOUT_TIME," seconds )" )
                self.dbst=stEnum.ERROR;
            elif self.query_result_available():
                self.val=self.get_database_response()
                self.dbst=stEnum.DONE
            return None,None        
        elif    self.dbst==stEnum.DONE:     
            self.dbst=stEnum.READY
            return True,self.val 
        elif  self.dbst== stEnum.ERROR:
            self.dbst=stEnum.READY
            print('In db_req_response, reporting database error')
            return False,None
            
    def db_request(self,cardID,machineID): 
        self.DATABASE_TIMEOUT_TIME=10
        self.request_cardID=cardID
        self.request_machineID=machineID
        if  self.dbst == stEnum.READY:    # beginning of the state machine
            self.query(cardID,machineID)        # send a query to data base
            self.tmer.set_time(self.DATABASE_TIMEOUT_TIME)   # set a timeout timer
            self.dbst=stEnum.SENT_REQUEST # update the state
            return True
        else:
            print("ERROR, called db_request, but we are in state  ", self.dbst)
            self.state= stEnum.ERROR
            return False  #signifies an error condition             
        
if  __name__ == "__main__": 
    print('HI there') 
    dfake=DataBase.DataBase()    
    d=DataBaseQuery(dfake)
    s1=1; s2=2; s3=3; s4=4; 
    ss=s1;

    while True:
        if ss==s1:
            OK=d.db_request("0080486","007")
            if OK==False:
                print('Screwed up request for database');
            if OK==True:
                print ('database request sent OK');
            ss=s2;                
        if ss==s2:
            # x=d.db_request("0080486","007")
            OK,val=d.db_req_response()
            if OK==True:
                print('finished with a good result, ',val)
                ss=s3
            if OK==False:
                print('finished with an error, let the database guys know')
                ss=s3; 
        if ss==s3:
            print('program is over')
            quit()
        
    
        
       