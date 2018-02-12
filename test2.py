import math 
class testclass:
    
    def  __init__(self):
        pass
        
 
    def method1(self,command):
        print("the result is ", command())
        
          
if  __name__ == "__main__": 
    print('HI there')     
    # define the serial port 
    ob=testclass()
    ob.method1(lambda: math.sin(3))
            