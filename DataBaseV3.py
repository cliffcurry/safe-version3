#REAL DATABASE 
# 
# this is the interface to the POSTGRESQL database 
#  set up as a three call process, this program structure is not used anymore because of the blocking nature of the queries.
#  I had originally thought the data base could be queried, then polled for a response, then the response would be retrieved.
#   however, it turns out the responses are actually blocking until the data is returned 
# works like this:  (1) from the calling program, a query comes in, specifying the database table and the ID, or lookup index. 
# (2) the calling program should poll the query result avaliable, when this is true, data has come in. 
# (3) when the result is avaliable, the program should call get database response.  this will provide the table information to the caller

import timeoutTimer
import timing_constants

import requests
import json    
        

class DataBase():
    
                        
    def __init__(self):
    
     
        self.table="machineInfo"
        self.ID="15"
        
        
            
            # the models of the database
        self.NEW_Interlock=dict( mac='06;7a;56;22;12' ,manufacturing_date='2019-09-14',controller_serial_number=5, relay_box_serial_number=8)
        self.NEW_Lab=dict( name='Machine shop', room='105 SC',start_time='5:00',end_time='18:00')
           
        # self.NEW_Person=dict(  university_id='7897987',kind_of_person='staff', name="Clifford Curry", start_date="2018-05-01", end_date="2018-12-01"
                             # ,start_time="8:00",
                            # end_time="14:30")
         # #  rather than have lists of users and supervisors for machines, one does a database lookup                        
        # self.NEW_Machine=dict(  machine_id='5',
                            # university_inventory_number='456-980-9870',manufacturer_serial_number='98797-988',
                            # name="Acme 2HP drill press", 
                            # lab_containing_machine="b-103", kind_of_swipe_needed="supervisor",start_time="3:00",
                            # end_time="8:45",
                            # minutes_enabled='30',uses_estop=False,
                            # )    
        ## other database tables: InterlockLookup, ProxcardLookup.
       
        # a mac address can retrieve all of this information... an interlock, a machine, and a lab.  here it is in one big query.                     
        self.NEW_Inter_Machine_Lab_INFO=dict(  manufacturing_date='2015-06-01',controller_serial_number=4,relay_box_serial_number=7,
                            university_inventory_number='456-980-9870',manufacturer_serial_number='98797-988',
                            machine_id='5', name="Acme 2HP drill press", 
                            lab_containing_machine="b-103", kind_of_swipe_needed="supervisor",start_time="3:00",
                            end_time="8:45",
                            minutes_enabled='30',uses_estop=False,
                            lab_name='machine shop',
                            lab_room='b107 SC',
                            lab_start_time='5:00',
                            lab_end_time='15:23')    
        
        
    ############# call the following function at the beginning of the program!!!!!        
    # returns all the info about the interlock, about the machine, and about the lab the machine is in
    
    DATABASE_LOCATION= 'appdev001.engr.uiowa.edu'
    #DATABASE_LOCATION= '172.17.7.172:8080'
    def info_from_mac(self,ID):
        preamble='https://'+self.DATABASE_LOCATION+'/ui/get_machine_lab_from_mac/'
        request_string=preamble+ID
        print("Database query is ",request_string)
        try:
            response=requests.get(request_string, timeout=10)
        except requests.exceptions.Timeout:
            print('Timeout exception.. database server not responding')
            return None
        except requests.exceptions.TooManyRedirects:    
            print(' Likely your database URL is bad, try a different one')
            return None
        except requests.ConnectionError as e:
            print('Connection error to database ')
            print(e)
            return None
        except requests.exceptions.RequestException as e:
            print('Catastrophic error communicationg to database ')
            print(e)
            return None
        
        
        
        
        if response.status_code==200:
            #self.NEW_Inter_Machine_Lab_INFO=  json.loads(response.text)
         
            return json.loads(response.text)
        else:
            print("ERROR, MAC address %s is  not in database" % ID )     
            return None    
                
    ############# call the following function whenever a card is swiped      
    # returns all the info about the person who owns the card 
    
    def info_from_prox(self,ID):
        preamble='https://'+self.DATABASE_LOCATION+'/ui/person_from_prox_card/'
        request_string=preamble+ID
        try:
            response=requests.get(request_string, timeout=10)
        except requests.exceptions.Timeout:
            print('Timeout exception.. database server not responding')
            return None
        except requests.exceptions.TooManyRedirects:    
            print(' Likely your database URL is bad, try a different one')
            return None
        except requests.ConnectionError as e:
            print('Connection error to database ')
            print(e)
            return None
        except requests.exceptions.RequestException as e:
            print('Catastrophic error communicationg to database ')
            print(e)
            return None
        
      
        if response.status_code==200:
            return json.loads(response.text)
        else:
            print("ERROR, prox card %s is  not in database" % ID )  
            return None    
              
          
                        
    def first_swipe(self,proxID,mac):
        preamble='https://'+self.DATABASE_LOCATION+'/ui/first_swipe_access/'
        request_string=preamble+proxID+'/'+mac
        
        try:
            response=requests.get(request_string, timeout=10)
        except requests.exceptions.Timeout:
            print('Timeout exception.. database server not responding')
            return None
        except requests.exceptions.TooManyRedirects:    
            print(' Likely your database URL is bad, try a different one')
            return None
        except requests.ConnectionError as e:
            print('Connection error to database ')
            print(e)
            return None
        except requests.exceptions.RequestException as e:
            print('Catastrophic error communicationg to database ')
            print(e)
            return None
        
        if response.status_code==200:
            print('RESPONSE=',response.text)
            (lhs,sep,rhs)=response.text.partition(',')
            if lhs=='GRANTED' :
                return(True,rhs.lstrip())
            else:
                return(False,rhs.lstrip())
        else:
            print("ERROR, prox card %s or MAC %s not in database" % (proxID,mac))
            return None
    
    def second_swipe(self,proxID,proxID2,mac):
        preamble='https://'+self.DATABASE_LOCATION+'/ui/second_swipe_access/'
        request_string=preamble+proxID+'/'+proxID2+'/'+mac
        try:
            response=requests.get(request_string, timeout=10)
        except requests.exceptions.Timeout:
            print('Timeout exception.. database server not responding')
            return None
        except requests.exceptions.TooManyRedirects:    
            print(' Likely your database URL is bad, try a different one')
            return None
        except requests.ConnectionError as e:
            print('Connection error to database ')
            print(e)
            return None
        except requests.exceptions.RequestException as e:
            print('Catastrophic error communicationg to database ')
            print(e)
            return None
        
        if response.status_code==200:
            (lhs,sep,rhs)=response.text.partition(',')
            if lhs=='GRANTED' :
                return(True,rhs.lstrip())
            else:
                return(False,rhs.lstrip())
        else:
            print("ERROR, status=%s. prox card %s, prox card %s, or MAC %s not in database" % (response.status_code,proxID,proxID2,mac)) 
            return None
    
    
    
    # called from the database query module, as the first thing of the state machine, this routine really does not do anything 
    
    def query(self,table,ID,ID2='00000',MAC='02:89:78'):
        self.table=table; self.ID=ID ; self.ID2=ID2;self.MAC=MAC

    #  this is meant to be called repeatedly in the second part of the state machine: return false if data is no good and true if data is ready.    
        
    def query_result_available(self):
        return True
    #    this is called after the calling program (databasequery) has gotten a true result from the available routine. It really returns the data     
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
        elif self.table=="first_swipe_access":
            return(self._firstSwipe(self.ID,self.ID2))
        elif self.table=="second_swipe_access":
            return(self._secondSwipe(self.ID,self.ID2,self.MAC) )   
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
       
       
