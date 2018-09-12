import tkinter as tk

import globs
import time
import calculations
class Display():
    #global callback
    def __init__(self,master):
        
        self.master=master
        self.wdth=22; self.hgt=5    
        self.tbox = tk.Text(master, width=self.wdth,height=self.hgt)
        globs.my_mac_address=calculations.get_mac_addr()
        self.tbox.config(bg='lightgreen', font=('courier', 70  , 'bold'))  
        ist=''
        for i in range(0,self.hgt):
            ist=ist+'\n'
        self.tbox.insert('0.0',ist)
        self.tbox.pack()
        self.tbox.bind('<Motion>',self.callback)  
        self.display_message_to_user('Version='+globs.SOFTWARE_VERSION,1)
        self.display_message_to_user('MAC='+globs.my_mac_address,2)
        self.master.update_idletasks()
        self.master.update()
        
    def callback(self,event):

        #print('Tk callback entered. flag=' ,globs.user_touched_screen_flag) 
        globs.user_touched_screen_flag=True
        #print('Tk callback has been executed. flag=' ,globs.user_touched_screen_flag) 
        
    def change_background(self):
        self.tbox.config(bg='white')
    def reset_background(self):
        self.tbox.config(bg='lightgreen')
        
    def display_message_to_user(self,message,line):
        if line<=self.hgt:
            s='%d.0' % line
            e='%d.end' % line
            self.tbox.delete(s,e)
            new_message=message.replace('\n',' ')
            self.tbox.insert(s,new_message[:self.wdth])
            self.tbox.pack()
            self.master.update_idletasks()
            self.master.update()
        else:
            print('ERROR in writing to display')
  
if  __name__ == "__main__": 
    globs.user_touched_screen_flag=False;
    
    print('HI there')
    displayscreen = tk.Tk()
    displayscreen.overrideredirect(True)
    Dis=Display(displayscreen);
    x=0
    dell=1000000/2
    while x<10*dell :  ### loop for a long time 
        displayscreen.update_idletasks()
        displayscreen.update()
        x=x+1
        if globs.user_touched_screen_flag==True:
            globs.user_touched_screen_flag=False
            x=10*dell
        
        if x==dell: 
            Dis.display_message_to_user("abcdefghijklmnopqrstuvwxyz",2)
            print(x)
            Dis.display_message_to_user('These \n  times that \n line',3)
            Dis.display_message_to_user('line 4',4)
            
        if x==2*dell: 
            
            print(x)
        if x==3*dell:              
            if True:
                Dis.display_message_to_user('Supervisor req.',2);
                Dis.display_message_to_user('Ask the supervisor',3)
            elif 0==5:
                Dis.display_message_to_user('2nd Student Swipe req.',2);
                Dis.display_message_to_user('Ask another student',3)  
            Dis.display_message_to_user('to swipe card.',4)
            Dis.display_message_to_user('-----test message----- ',5)
            line=0
            print(x)

        if ((x % dell)==0) and x>3*dell: 
            line=line+1
            Dis.display_message_to_user("New Line %d -" % (line) ,line)
            print(x)    
                    
                    
                
