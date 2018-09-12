from enum import Enum
import datetime
import DataBaseV2
import DataBaseQuery
import globs
            
def tominutes(x):
    if isinstance(x,str):
        partuple=x.partition(':')
        hrs=int(partuple[0])
        mins=int(partuple[2])
        return (mins+60*hrs)
    elif isinstance(x,datetime.datetime):    
        print('to minutes time now is ',x.hour,':',x.minute)
        corhour=x.hour
        #corhour=corhour
        return (x.minute+60*corhour)

# utility for mac addresses 
def mac_clean(mac): 
    return((mac.strip(' :-.').lower()).replace(' ','').replace('-',':'))
   
def mac_match(mac1,mac2):
    return (mac_clean(mac1)==mac_clean(mac2))
            
 
 
import netifaces
def get_mac_addr():
    interfaces=netifaces.interfaces()
# ['lo', 'eth0', 'tun2']

    listofstuff=netifaces.ifaddresses(interfaces[2])[netifaces.AF_LINK]
# [{'addr': '08:00:27:50:f2:51', 'broadcast': 'ff:ff:ff:ff:ff:ff'}]
    macadd=listofstuff[0]['addr']
    print("In mac address, returned mac is ",mac_clean(macadd))
    
    return mac_clean(macadd)
    

    


     
            
        
def time_for_access(actual_start_time, actual_end_time,minutes_enabled):
    time_now= tominutes(datetime.datetime.now())
    if actual_start_time>time_now:
        return 0
    else:    
        max_time_left=actual_end_time-time_now
        if max_time_left<0:
            max_time_left=0
        time_to_give_access=min((max_time_left),minutes_enabled)
        return time_to_give_access
       

def check_start_time(minutesnow,mtable,ptable,ltable):
        OK=True; reason="None"
        if minutesnow<tominutes(mtable["start_time"]):
            OK=False; reason="Too Early for machine"
        if minutesnow<tominutes(ptable["start_time"]):
            OK=False; reason="Too Early for User"
        if minutesnow<tominutes(ltable["start_time"]):
            OK=False; reason="Too Early for lab"
        return (OK,reason)


def check_end_time(minutesnow,mtable,ptable,ltable):
        OK=True; reason="None"
        if minutesnow>tominutes(mtable["end_time"]):
            OK=False; reason="Too Late for machine"
        if minutesnow>tominutes(ptable["end_time"]):
            OK=False; reason="Too Late for User"
        if minutesnow>tominutes(ltable["end_time"]):
            OK=False; reason="Too Late for lab"
        return (OK,reason)
                
                
                
                
      
if  __name__ == "__main__": 

    print('HI there') 
    mac='  C5:78:  98-99:B6:- . '
    print("mac=",mac)
    print("fixed=",mac_clean(mac))
    print(mac_match('67-98-bc- 45-99','67:98:BC:45:99:-:'))
    
    print('original=',get_mac_addr())
     
    print('fixed up=',mac_clean(get_mac_addr()))
    print(mac_match(get_mac_addr(),mac_clean(get_mac_addr())))

