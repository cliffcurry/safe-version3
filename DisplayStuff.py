import tkinter as tk
import globs
import time
class Display():
    #global callback
    def __init__(self,master):
        
        self.master=master
            
        self.tbox = tk.Text(master, width=22,height=5)
        
        self.tbox.config(bg='lightgreen', font=('times', 84  , 'bold'))    
        init_text= "Software version 0.8\n\n\n\n"
        display_text = tk.StringVar()
        display_text.set(init_text);
        
        self.tbox.insert('0.0',init_text);
        self.tbox.pack()
        self.tbox.bind('<Motion>',self.callback)  
        self.master.update_idletasks()
        self.master.update()
        
    def callback(self,event):

        print('Tk callback entered. flag=' ,globs.user_touched_screen_flag) 
        globs.user_touched_screen_flag=True
        print('Tk callback has been executed. flag=' ,globs.user_touched_screen_flag) 
    def display_message_to_user(self,message,line):
        
        if line==1:
            s='1.0'
            e='1.end'
        elif line==2:
            s='2.0'
            e='2.end'
        elif line==3:
            s='3.0'
            e='3.end'
        elif line==4:
            s='4.0'
            e='4.end'
        elif line==5:
            s='5.0'  
            e='5.end'    
        self.tbox.delete(s,e)
        self.tbox.insert(s,message)
        self.tbox.pack()

        self.master.update_idletasks()
        self.master.update()
           
    

        
  
        
if  __name__ == "__main__": 
    globs.user_touched_screen_flag=False;
    #def callback(event):
        #print('Tk callback has been executed' )
        #global globs.user_touched_screen_flag
        #globs.user_touched_screen_flag=True;
    print('HI there')
    displayscreen = tk.Tk()
    displayscreen.overrideredirect(True)
    Dis=Display(displayscreen);
    x=10000000 
    while x>0 :
        displayscreen.update_idletasks()
        displayscreen.update()
        if globs.user_touched_screen_flag==True:
            globs.user_touched_screen_flag=False
            x=0
        x=x-1
    Dis.display_message_to_user("Line 1 \n Line two \n Line three \n Line four \n Line 5 ",1)
   
    y=x+10000000
    while y>0 :
        y=y-1
    Dis.display_message_to_user("New Line 2",2)
    x=10000000
    while x>0 :
        x=x-1
