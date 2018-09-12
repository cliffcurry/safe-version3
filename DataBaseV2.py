# program that simulates a real data base
# version two is like the microsoft word document 
# this is a fake database.  pass this class to the database query module 

# works like this:  (1) from the calling program, a query comes in, specifying the database table and the ID, or lookup index. 
# (2) the calling program should poll the query result avaliable, when this is true, data has come in. 
# (3) when the result is avaliable, the program should call get database response.  this will provide the table information to the caller

import timeoutTimer
import timing_constants

class DataBase():
   
    def __init__(self):
        self.delay_expired=False
        self.tmer=timeoutTimer.timeoutTimer()
        self.table="machineInfo"
        self.ID="15"
    
   
        
    def _proxcardlookup(self,ID):
        if ID=="0080486" : # cliff
            return "123456"
        elif ID=="0158076" : # brian
            return "34567"
        elif ID=="0069405" : # zane Brewer
            return "123"
        elif ID=="0090001" : # john
            return "22"    
        elif ID=="00113371" : # mike Hillman
            return "23"        
        elif ID=="0090031" : # tom
            return "24"     
        elif ID=="0082301" : # chris
            return "25"
        elif ID=="0126170" : # diem
            return "26"    
        else:
            print("ERROR, prox card not in database")
    def _interlocklookup(self,ID):
        if ID=="b8:27:eb:f7:59:90":
            return "17"
        if ID=="28-B2-BD-50-50-F9":
            return "16"
        if ID=="00:50:56:c0:00:01":
            return "15"
        if ID=="00:50:56:c0:00:08":
            return "17"
        if ID=="b8:27:eb:60:4a:42":   # this is number two 
            return "18"    
        if ID=="b8:27:eb:14:1a:31":   # this is number three
            return "19"   
    def _labInfo(self,ID):
        if ID=="b-103":
            return dict(name="DFM lab, basement", start_time="8:00",
                        end_time="15:00")
            
        if ID=="Machine Shop": 
            return dict(name="Machine Shop, basement",start_time="7:10",
                        end_time="17:30")
                    
            
    def _machineInfo(self,ID):
        if ID=="15":
            return dict(name="Acme 2HP drill press", lab="b-103", kind_of_swipe_needed="supervisor",start_time="3:00",
                        end_time="8:45",personAccessList=["123456","34567","39876"],supervisorAccessList=["3456","78955","97335","34567"],
                        minutes_enabled=30,uses_estop=False)
        if ID=="16": 
            return dict(name="Haart mill", lab="machine_shop", kind_of_swipe_needed="Single",start_time="1:00",
                        end_time="18:30",personAccessList=["31456","134567","3898"],supervisorAccessList=["53456","878955","565","34567"],
                        minutes_enabled=11,uses_estop=False)
        if ID=="17":   ###### THIS IS THE ONE CHOZEN NOW
            return dict(name="Acme SuperGrinder", lab="b-103", kind_of_swipe_needed="SecondStudent",start_time="7:00",
                        end_time="17:00",personAccessList=[ "123456","0158076","34567","123","22","23","24","25","26" ],supervisorAccessList=[ "123","123456","0158076","26" ],
                        minutes_enabled=4,uses_estop=False)
        if ID=="18":   ###### THIS IS THE one for device 002
            return dict(name="Jet Mill/Drill", lab="Machine Shop", kind_of_swipe_needed="Single",start_time="7:00",
                        end_time="16:30",personAccessList=[ "123456","0158076","34567","123","22","23","24","25","26" ],supervisorAccessList=[ "123","123456","0158076","26" ],
                        minutes_enabled=25,uses_estop=False)   
        if ID=="19":   ###### THIS IS THE one for device 003
            return dict(name="HiTorque Bench Lathe", lab="Machine Shop", kind_of_swipe_needed="Single",start_time="7:00",
                        end_time="16:30",personAccessList=[ "123456","0158076","34567","123","22","23","24","25","26" ],supervisorAccessList=[ "123","123456","0158076","26" ],
                        minutes_enabled=15,uses_estop=False)     
        
    def _personInfo(self,ID):
        if ID=="123456": #cliff 
            return dict(name="Clifford Curry", kind_of_person="checked",start_time="8:00",
                        end_time="14:30")
        elif ID=="34567": # brian 
            return dict(name="Brian Snider", kind_of_person="allAccess",start_time="7:00",
                        end_time="18:30")
        elif ID=="22": # john
            return dict(name="John Kostman", kind_of_person="checked",start_time="7:00",
                        end_time="15:30")
        elif ID=="123": # zane
            return dict(name="Zane Brewer", kind_of_person="allAccess",start_time="7:00",
                        end_time="15:30")
        elif ID=="23": # mike
            return dict(name="Mike Hillman", kind_of_person="allAccess",start_time="11:00",
                        end_time="15:30")
        elif ID=="24": # tom
            return dict(name="Tom Barnhart", kind_of_person="checked",start_time="9:00",
                        end_time="18:30")                
        elif ID=="25": # chris
            return dict(name="Chris Corestopolis", kind_of_person="checked",start_time="7:00",
                        end_time="11:30")  
        elif ID=="26": # Diem
            return dict(name="Diem Nguyen", kind_of_person="checked",start_time="13:00",
                        end_time="15:30")  
                        
    def query(self,table,ID):
        self.table=table
        self.ID=ID
        self.tmer.set_time(timing_constants.FAKE_DB_DELAY_TIME)   # sets the delay between a request is sent and this program return the result 
       
        
    def query_result_available(self):
        if not self.tmer.timed_out():
            return False
        else:
            self.tmer.reset();
            return True
        
    def get_database_response(self):
        if self.table=="machineInfo":
            return(self._machineInfo(self.ID))
        elif self.table=="personInfo":
            return(self._personInfo(self.ID))
        elif self.table=="labInfo":
            return(self._labInfo(self.ID))
        elif self.table=="proxcardlookup":
            return(self._proxcardlookup(self.ID))
        elif self.table=="interlocklookup":
            return(self._interlocklookup(self.ID))
        else:
            print("ERROR in database call, table undefined")
            return None
                
            
            
            
            
           
        
            
  
      
if  __name__ == "__main__": 
    print('HI there')     
    d=DataBase()
    
    listofcards=["0080486","0158076","0069405","0090001","00113371","0090031","0082301","0126170"]

    for proxcardID in listofcards: 
        # proxcardID="0080486" 
                                       
        personID=d._proxcardlookup(proxcardID)
        print("personID=",personID)
        personTable=d._personInfo(personID)  
        print("personTable=",personTable)
        
    listofmacaddress= [ "74-46-A0-96-DB-D2","00:50:56:c0:00:01",  "b8:27:eb:f7:59:90"  ] 
    for interlockID in listofmacaddress: 
        
        machineID=d._interlocklookup(interlockID)
        print("machineID=",machineID)
        if machineID !=None:
            machineTable=d._machineInfo(machineID)
            print("machineTable=",machineTable) 
            if machineTable !=None:
                labTable=d._labInfo(machineTable["lab"])
                print("labTable=",labTable)
       
       
