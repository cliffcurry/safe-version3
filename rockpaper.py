from tkinter import *
from ttk import *
import random
import sys

##def makeYourChoice():
##    print "Press R for Rock"
##    print "Press P for Paper"
##    print "Press S for Scissors"
##    print "Press Q to quit!"
##
##    userChoice = raw_input("What do you want to choose?").lower()
##    
##    ### Using if rather then elif
##    if userChoice == "r":
##        return "Rock"
##    if userChoice == "p":
##        return "Paper"
##    if userChoice == "s":
##        return "Scissors"
##    if userChoice == "q":
##        sys.exit(0)
##        
##    else:
##        makeYourChoice()

def computerRandom():
    options = ["Rock","Paper","Scissors"]
    randomChoice = random.randint(0,2)
    computer_choice.set(options[randomChoice]) ##added into the program
    return options[randomChoice]

def comparison(humanChoice, computerChoice):
    if humanChoice == computerChoice:
        return "Draw"
    if humanChoice == "Rock" and computerChoice == "Paper":
        return "Computer Wins"
    if humanChoice == "Paper" and computerChoice == "Scissors":
        return "Computer Wins"
    if humanChoice == "Scissors" and computerChoice == "Rock":
        return "Computer Wins"
    else: return "Human Wins"

def play():

    
    humanChoice = player_choice.get() ##Modified this line
    computerChoice =  computerRandom()

    #print player_choice.get() ## This line is no longer needed
    #print computer_choice.get() ## This line is no longer needed
    
##    if player_choice.get() != '':
    ## Indent lines below if line above is uncommented.    
        
    result = comparison(humanChoice, computerChoice)

    if result == "Draw":
        result_set.set("Its a draw")
    elif result == "Computer Wins":
        result_set.set("Unlucky you lost!")
    else:  result_set.set("Well done you won!")
        
##    else:
##        result_set.set("Please choose an option")
  
    

##while True:
    
##    humanChoice = makeYourChoice()
##    computerChoice =  computerRandom()
##
##    print "You chose", humanChoice
##    print "The computer chose", computerChoice
##
##    result = comparison (humanChoice, computerChoice)
##
##    if result == "Draw":
##        print "Its a draw"
##    elif result == "Computer Wins":
##        print "Unlucky you lost!"
##    else: print "Well done you won!"
##
##    print " "

##Setup of main GUI
root = Tk()
root.title ('Rock Paper Scissors')

mainframe = Frame(root, padding = '3 3 12 12')
mainframe.grid(column=0, row = 0, sticky=(N,W,E,S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0,weight=1)

##Variables
player_choice = StringVar()
computer_choice = StringVar()
result_set = StringVar()
#player_choice.set("Rock")  ## Required to set player as "Rock" by default

##Layout of GUI
##Player
Label(mainframe, text='Player').grid(column=1, row = 1, sticky = W)
Radiobutton(mainframe, text ='Rock', variable = player_choice, value = 'Rock').grid(column=1, row=2, sticky=W)
Radiobutton(mainframe, text ='Paper', variable = player_choice, value = 'Paper').grid(column=1, row=3, sticky=W)
Radiobutton(mainframe, text ='Scissors', variable = player_choice, value = 'Scissors').grid(column=1, row=4, sticky=W)

##Computer
Label(mainframe, text='Computer').grid(column=3, row = 1, sticky = W)
Radiobutton(mainframe, text ='Rock', variable = computer_choice, value = 'Rock').grid(column=3, row=2, sticky=W)
Radiobutton(mainframe, text ='Paper', variable = computer_choice, value = 'Paper').grid(column=3, row=3, sticky=W)
Radiobutton(mainframe, text ='Scissors', variable = computer_choice, value = 'Scissors').grid(column=3, row=4, sticky=W)

##Play
Button(mainframe, text="Play", command = play).grid(column = 2, row = 2, sticky = W)

##Result
Label(mainframe, textvariable = result_set).grid(column = 1, row = 5, sticky =W, columnspan = 2)

root.mainloop()
