# interface to the data base.  
# program that timeouts the database queries

import timing_constants
import timeoutTimer
import DataBaseV3
from enum import Enum





class DataBaseQuery:  #pass it the database class, which has query, available functions built into it. 
 
    
    class stEnum(Enum):

        READY=0
        SENT_REQUEST =2
        DONE = 5
        ERROR = 6
      
    def __init__(self,db):
        
        self.database=db
     
    def second_swipe(self,ID,ID2,ID3):
        (OK,reason)=self.database.second_swipe(ID,ID2,ID3)
        return(OK,reason) 
    def first_swipe(self,ID,ID2):
        (OK,reason)=self.database.first_swipe(ID,ID2)
        return(OK,reason) 
    def info_from_mac(self,mac):
        return(self.database.info_from_mac(mac))
          #return self.database.NEW_Inter_Machine_Lab_INFO
    def info_from_prox(self,prox):
        return self.database.info_from_prox(prox)
        
    
        
if  __name__ == "__main__": 
    print('HI there') 
    dfake=DataBaseV3.DataBase()    
    d=DataBaseQuery(dfake)
    mmac='74:46:a0:96:db:d2'
    
    stuff=d.info_from_mac(mmac)
    
    print(stuff)
    morestuff=d.info_from_prox("0080486")
    print(morestuff)
    
    (OK,reason)=d.first_swipe("0080486",mmac)
    print(OK)
    print(reason)


    OK,val=d.second_swipe("0080486","0090031",mmac)
    print(OK)
    print(reason)
               

    print('program is over')
    quit()
        
    
        
       