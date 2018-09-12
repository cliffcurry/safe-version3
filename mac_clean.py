

def mac_clean(mac): 
    return((mac.strip(' :-.').lower()).replace(' ','').replace('-',':'))
   
def mac_match(mac1,mac2):
    return (mac_clean(mac1)==mac_clean(mac2))
    
  
        
if  __name__ == "__main__": 
    print('HI there') 
    mac='  C5:78:  98-99:B6:- . '
    print("mac=",mac)
    print("fixed=",mac_clean(mac))
    print(mac_match('67-98-bc- 45-99','67:98:BC:45:99:-:'))
     
    
       