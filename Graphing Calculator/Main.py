from random import randint
import sys
from sys import exit
import math
import random
import pygame
import sqlite3
import time
import re
import ShuntingYard


#pygame must be initialised in order to utilise the modules it has
pygame.init()

#creating connection to database
con = sqlite3.connect("GraphingCalc.db")
cursor = con.cursor()

#creates the tables in the database if they don't exist
con.execute("""CREATE TABLE if not exists Functions (
              Function_Num INTEGER,
              Function STRING,
              CONSTRAINT Functions_pk PRIMARY KEY (Function_Num)
              )""")

con.execute("""
              CREATE TABLE if not exists YIntercepts (
              Function_YInt_ID INTEGER,              
              YIntercept_Value REAL,
              FOREIGN KEY(Function_YInt_ID) REFERENCES Functions(Function_Num)
              )""")

con.execute("""
              CREATE TABLE if not exists Colours (
              Colour STRING,
              Colour_Func_ID INTEGER,
              FOREIGN KEY(Colour_Func_ID) REFERENCES Functions(Function_Num)
              )""")

con.execute("""
              CREATE TABLE if not exists Integration (
              UB FLOAT,
              LB FLOAT,
              Integral FLOAT,
              Integral_Func_ID INTEGER,
              FOREIGN KEY(Integral_Func_ID) REFERENCES Functions(Function_Num)
              )""")
con.commit()

#clearing the data from the database if the user has inputted values in the graphing calculator before
con.execute("""pragma foreign_keys=off;""")
con.execute("""DELETE FROM Functions WHERE Function_Num = 1""")
con.execute("""DELETE FROM Functions WHERE Function_Num = 2""")
con.execute("""DELETE FROM YIntercepts WHERE Function_YInt_ID = 1""")
con.execute("""DELETE FROM YIntercepts WHERE Function_YInt_ID = 2""")
con.execute("""DELETE FROM Colours WHERE Colour_Func_ID = 1""")
con.execute("""DELETE FROM Colours WHERE Colour_Func_ID = 2""")
con.execute("""DELETE FROM Integration WHERE Integral_Func_ID = 1""")
con.execute("""DELETE FROM Integration WHERE Integral_Func_ID = 2""")
con.commit()

#set up pygame window
pygame.display.set_caption("Calculator")
windowSurface = pygame.display.set_mode((600, 600))
mainClock = pygame.time.Clock()

font = pygame.font.Font(None, 35)

def check(eqn,funcnum): #this function checks the users input
    eqn = eqn.split()
    eqn = "".join(eqn)
    for var in eqn:
        if var == 'y':  # this condition checks for any characters other than x in the user input and displays a message to tell the user
            errorlabel = font.render("function must be explicit", 10, 'red')
            windowSurface.blit(errorlabel, (300,0))
            pygame.display.flip()
            time.sleep(1.5)
            Main()
        else:
            continue
            
def formatEqn(rawEqn,funcnum): #this function formats the users input function into a form that python can evaluate
    func = rawEqn.replace(" ", "")
    func = re.sub(r"x\^(\d)", r"x**\1", func) #changes instances such as x^2 to x**2
    func = re.sub(r"\be\^x\b", r"e**x", func) #changes instances such as e^x to e**x
    func = re.sub(r"(\d)x", r"\1*x", func) #changes instances such as 2x to 2*x
    func = re.sub(r"\b(sin|cos|tan)\b", r"math.\1(", func) #changes instances such as tan(x) to math.tan(x)
    func = re.sub(r"(sin|cos|tan)\(\(\s*", r"\1(", func)
    func = re.sub(r"(\d|\))\(", r"\1*(", func) #changes instances such as 3(9+3) to 3*(9+3)
    func = re.sub(r"(\d)e", r"\1*e", func) #changes instances such as 2e to 2*e
    func = re.sub(r"\)(\d|x)", r")*\1", func) ##changes instances such as x2 to x*2
    try:
            for log in ["e", "log"]: #replaces log and  written by user into e.math() and log.math() which python can understand and evaluate
                    if log in func: #log and e have to be in a try, except clause as they dont go past 0
                            if log == "log" and "log(" not in func:
                                    func = func.replace(log, "".join(["math.", log, "("]))
                            else:
                                    func = func.replace(log, "".join(["math.", log]))
            if func == "": #if the user enters nothing then the program just returns 0                
                con.execute("""INSERT INTO Functions (Function_Num, Function) VALUES(?,?)""", [funcnum, 0]) #parameterised query places the function with it's respective number
                con.commit()
            else: #inputs the formatted function into the database               
                con.execute("""INSERT INTO Functions (Function_Num, Function) VALUES(?,?)""", [funcnum, func]) #parameterised query places the function with it's respective number
                con.commit()
    except:
            pass
         



def Main(): #this sets up the GUI, it allows the user to input their function and, when the user clicks any buttons on the screen, it takes them to
    #their desired screen
    funcinput1 = '' #user input strings, within the function these are appended to when the user enters a function
    funcinput2 = ''
    colourinput1 = ''#or a colour
    colourinput2 = ''
    ubinput1 = ''
    lbinput1 = ''
    ubinput2 = ''
    lbinput2 = ''
    

    funcrectangleinput1 = pygame.Rect(100,400,140,32) #these set up the coordinates of the input boxes on the screen
    funcrectangleinput2 = pygame.Rect(100,450,140,32)
    colourrectangleinput1 = pygame.Rect(100,350,140,32)
    colourrectangleinput2 = pygame.Rect(100,500,140,32)
    ubrectangleinput1 = pygame.Rect(260,400,20,20)
    lbrectangleinput1 = pygame.Rect(340,400,20,20)
    ubrectangleinput2 = pygame.Rect(260,450,20,20)
    lbrectangleinput2 = pygame.Rect(340,450,20,20)
    logo = pygame.image.load('Logo.jpg') #loads the logo saved in the file
    
    #these are the colours of the input boxes when they are clicked and not clicked
    colouractive = pygame.Color('purple')
    colourinactive = pygame.Color('pink')
    colour = colourinactive

    colouractive2 = pygame.Color('purple')
    colourinactive2 = pygame.Color('pink')
    colour2 = colourinactive2

    colouractive3 = pygame.Color('purple')
    colourinactive3 = pygame.Color('pink')
    colour3 = colourinactive3

    colouractive4 = pygame.Color('purple')
    colourinactive4 = pygame.Color('pink')
    colour4 = colourinactive4

    
    #these booleans are used to figure out which box the user is inputting into
    active1 = False
    active2 = False
    active3 = False
    active4 = False
    active5 = False
    active6 = False
    active7 = False
    active8 = False

    #event handling in pygame, used to recognise when the user clicks a certain button or clicks a certain button on their keyboard

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN: #if input box is clicked, change it to active so the user can input their functions/colours
                if funcrectangleinput1.collidepoint(event.pos):
                    active1 = True
                else:
                    active1 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if funcrectangleinput2.collidepoint(event.pos):
                    active2 = True
                else:
                    active2 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if colourrectangleinput1.collidepoint(event.pos):
                    active3 = True
                else:
                    active3 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if colourrectangleinput2.collidepoint(event.pos):
                    active4 = True
                else:
                    active4 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if ubrectangleinput1.collidepoint(event.pos):
                    active5 = True
                else:
                    active5 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if lbrectangleinput1.collidepoint(event.pos):
                    active6 = True
                else:
                    active6 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if ubrectangleinput2.collidepoint(event.pos):
                    active7 = True
                else:
                    active7 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if lbrectangleinput2.collidepoint(event.pos):
                    active8 = True
                else:
                    active8 = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if drawbutton.collidepoint(event.pos): #when graph button is clicked 
                    #inserts colours into database
                    if colourinput1 == '': #this condition inserts preset colours if the user doesn't enter anything
                        con.execute("""INSERT INTO Colours (Colour, Colour_Func_ID) VALUES(?,?)""", ['red', 1])
                        con.execute("""INSERT INTO Colours (Colour, Colour_Func_ID) VALUES(?,?)""", ['green', 2])
                    else: #this condition enters the user inputted colours
                        con.execute("""INSERT INTO Colours (Colour, Colour_Func_ID) VALUES(?,?)""", [colourinput1, 1])
                        con.execute("""INSERT INTO Colours (Colour, Colour_Func_ID) VALUES(?,?)""", [colourinput2, 2])

                    if len(ubinput1) == 0 and len(lbinput1) == 0 and len(lbinput2) == 0 and len(ubinput2) == 0:
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [0,0, 1])
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [0,0, 2])
                        con.commit()
                    elif len(ubinput1) == 0 and len(lbinput1) == 0:
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [ubinput2,lbinput2, 2])
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [0,0, 1])
                        con.commit()
                    elif len(lbinput2) == 0 and len(ubinput2) == 0:
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [ubinput1,lbinput1, 1])
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [0,0, 2])
                        con.commit()
                    else:
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [ubinput1,lbinput1, 1])
                        con.execute("""INSERT INTO Integration (UB, LB, Integral_Func_ID) VALUES(?,?,?)""", [ubinput2,lbinput2, 2])
                        con.commit()
                    
                    check(funcinput1, 1) #users 1st function input is checked
                    check(funcinput2, 2) #users 2nd function input is checked
                    formatEqn(funcinput2, 2) #the function is formatted into a form that is able to be evaluated by python
                    formatEqn(funcinput1, 1)
                    calculateintegrals()
                    clearscreen() #clears the screen so the grid can be drawn
                    drawGrid() #draws the grid
                    GraphFunction1() # this then draws the function onto the grid.=
                    return
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if calcbutton.collidepoint(event.pos): #when calculator button is clicked
                    clearscreen() #the screen is cleared
                    calculatorscreen() #the calculator screen is drawn
                    return    
                
            if event.type == pygame.KEYDOWN: #these eight conditions are the same but they are exclusively for each input
                if active1 == True:
                    if event.key == pygame.K_BACKSPACE: #this condition is used to delete any characters the user wishes to delete from their function input
                        funcinput1 = funcinput1[:-1]
                    else:
                        funcinput1 += event.unicode #this condition adds any characters the user wishes to add to their function input

            if event.type == pygame.KEYDOWN:
                if active2 == True:
                    if event.key == pygame.K_BACKSPACE:
                        funcinput2 = funcinput2[:-1]  #this condition is used to delete any characters the user wishes to delete from their function input
                    else:
                        funcinput2 += event.unicode#this condition adds any characters the user wishes to add to their function input

            if event.type == pygame.KEYDOWN:
                if active3 == True:
                    if event.key == pygame.K_BACKSPACE:
                        colourinput1 = colourinput1[:-1]  #this condition is used to delete any characters the user wishes to delete from their colour input
                    else:
                        colourinput1 += event.unicode #this condition adds any characters the user wishes to add to their colour input

            if event.type == pygame.KEYDOWN:
                if active4 == True:
                    if event.key == pygame.K_BACKSPACE:
                        colourinput2 = colourinput2[:-1] #this condition is used to delete any characters the user wishes to delete from their colour input
                    else:
                        colourinput2 += event.unicode #this condition adds any characters the user wishes to add to their colour input

            if event.type == pygame.KEYDOWN:
                if active5 == True:
                    if event.key == pygame.K_BACKSPACE:
                        ubinput1 = ubinput1[:-1] #this condition is used to delete any characters the user wishes to delete from their colour input
                    else:
                        ubinput1 += event.unicode

            if event.type == pygame.KEYDOWN:
                if active6 == True:
                    if event.key == pygame.K_BACKSPACE:
                        lbinput1 = lbinput1[:-1] #this condition is used to delete any characters the user wishes to delete from their colour input
                    else:
                        lbinput1 += event.unicode

            if event.type == pygame.KEYDOWN:
                if active7 == True:
                    if event.key == pygame.K_BACKSPACE:
                        ubinput2 = ubinput2[:-1] #this condition is used to delete any characters the user wishes to delete from their colour input
                    else:
                        ubinput2 += event.unicode

            if event.type == pygame.KEYDOWN:
                if active8 == True:
                    if event.key == pygame.K_BACKSPACE:
                        lbinput2 = lbinput2[:-1] #this condition is used to delete any characters the user wishes to delete from their colour input
                    else:
                        lbinput2 += event.unicode
 
        windowSurface.fill((0,0,0))

        #this changes the colours of the boxes the user is currently inputting into 

        if active1 == True:
            colour = colouractive
        else:
            colour = colourinactive

        if active2 == True:
            colour2 = colouractive2
        else:
            colour2 = colourinactive2

        if active3 == True:
            colour3 = colouractive3
        else:
            colour3 = colourinactive3

        if active4 == True:
            colour4 = colouractive4
        else:
            colour4 = colourinactive4


        #these draw the input boxes to the screen

        pygame.draw.rect(windowSurface,colour,funcrectangleinput1,2)
        pygame.draw.rect(windowSurface,colour2,funcrectangleinput2,2)
        pygame.draw.rect(windowSurface,'white',ubrectangleinput1,2)
        pygame.draw.rect(windowSurface,'white',lbrectangleinput1,2)
        pygame.draw.rect(windowSurface,'white',ubrectangleinput2,2)
        pygame.draw.rect(windowSurface,'white',lbrectangleinput2,2)
        pygame.draw.rect(windowSurface,'white',colourrectangleinput1,2)
        pygame.draw.rect(windowSurface,'white',colourrectangleinput2,2)

        #these handle changing the box size when the user is inputting text, so that the box fits around the text. also handles the writing of text to the boxes

        functext_surface = font.render(funcinput1,True,(255,255,255))
        windowSurface.blit(functext_surface,(funcrectangleinput1.x + 5, funcrectangleinput1.y + 5))

        ub1text_surface = font.render(ubinput1,True,(255,255,255))
        windowSurface.blit(ub1text_surface,(ubrectangleinput1.x + 5, ubrectangleinput1.y + 5))

        lb1text_surface = font.render(lbinput1,True,(255,255,255))
        windowSurface.blit(lb1text_surface,(lbrectangleinput1.x + 5, lbrectangleinput1.y + 5))

        ub2text_surface = font.render(ubinput2,True,(255,255,255))
        windowSurface.blit(ub2text_surface,(ubrectangleinput2.x + 5, ubrectangleinput2.y + 5))

        lb2text_surface = font.render(lbinput2,True,(255,255,255))
        windowSurface.blit(lb2text_surface,(lbrectangleinput2.x + 5, lbrectangleinput2.y + 5))
        
        colourtext_surface = font.render(colourinput1,True,(255,255,255))
        windowSurface.blit(colourtext_surface,(colourrectangleinput1.x + 5, colourrectangleinput1.y + 5))

        functext_surface2 = font.render(funcinput2,True,(255,255,255))
        windowSurface.blit(functext_surface2,(funcrectangleinput2.x + 5, funcrectangleinput2.y + 5))

        colourtext_surface2 = font.render(colourinput2,True,(255,255,255))
        windowSurface.blit(colourtext_surface2,(colourrectangleinput2.x + 5, colourrectangleinput2.y + 5))

        funcrectangleinput1.w = max(100,functext_surface.get_width() + 10)
        funcrectangleinput2.w = max(100,functext_surface2.get_width() + 10)
        colourrectangleinput1.w = max(100,colourtext_surface.get_width() + 10)
        colourrectangleinput2.w = max(100,colourtext_surface2.get_width() + 10)


        drawbutton = pygame.Rect(250,550,100,32)
        calcbutton = pygame.Rect(430,400,150,50)
        #these label each input box
        ylabel = font.render("y=", 10, 'yellow')
        ublabel = font.render("UB:",8,'white')
        lblabel = font.render("LB:", 8, 'white')
        colourlabel = font.render("colour=",10,'white')
        calclabel = font.render("Calculator", 5, 'white') 
        drawlabel = font.render("Graph", 10, 'white')

        #these draw the objects (logo, labels, buttons) to the screen

        pygame.draw.rect(windowSurface,'blue',drawbutton)
        pygame.draw.rect(windowSurface,'blue',calcbutton)
        windowSurface.blit(ylabel, (65,400))
        windowSurface.blit(ylabel, (65,450))
        windowSurface.blit(ublabel, (215,450))
        windowSurface.blit(lblabel, (300,450))
        windowSurface.blit(ublabel, (215,400))
        windowSurface.blit(lblabel, (300,400))
        windowSurface.blit(colourlabel, (10,350))
        windowSurface.blit(colourlabel, (10,500))
        windowSurface.blit(calclabel, (440,410))
        windowSurface.blit(drawlabel, (260,555))
        windowSurface.blit(logo, (150, -20))
        pygame.display.flip()
        mainClock.tick(60)


def calculatorscreen():
    windowSurface = pygame.display.set_mode((300, 400)) #changes the size of the screen
    textinput = ''

    while True: #again event handling for this screen
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    textinput = textinput[:-1]
                else:
                    textinput += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                if exitbtn.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if enterbtn.collidepoint(event.pos): #when the user clicks on the enter button, it is sent to ShuntingYard.py
                    outputtext = ShuntingYard.ShuntingYard(textinput) 
                    displayoutput(outputtext) #which evaluates the expression and returns it to be displayed

        windowSurface.fill((0,0,0))

        #setting up the objects (labels, buttons) of the screen and drawing them to the screen

        enterbtn = pygame.Rect(115,300,80,35)
        exitbtn = pygame.Rect(115, 350, 80,35)
        pygame.draw.rect(windowSurface, 'blue',enterbtn)
        pygame.draw.rect(windowSurface, 'blue',exitbtn)
        exitlabel = font.render("Exit",20,'white')
        enterlabel = font.render("Enter",20,'white')
        windowSurface.blit(enterlabel,(123,305))
        windowSurface.blit(exitlabel,(125,355))

        inputrectangle = pygame.Rect(0,70,700,60)
        pygame.draw.rect(windowSurface, 'grey',inputrectangle,2)
        outputrectangle = pygame.Rect(0,165,700,60)
        pygame.draw.rect(windowSurface, 'grey',outputrectangle,2)
        inputlabel = font.render("Input:",15,'white')
        outputlabel = font.render("Output:",15,'white')
        windowSurface.blit(outputlabel,(3,140))
        windowSurface.blit(inputlabel,(3,40))


        text_surface = font.render(textinput,True,'white')
        windowSurface.blit(text_surface,(inputrectangle.x+5,inputrectangle.y+5)) 

        pygame.display.flip()



def displayoutput(outputtext): #displays the output on the calculator screen of the user inputted expression
    outputtextlabel = font.render(outputtext,20,'white')
    windowSurface.blit(outputtextlabel, (5,165))
    pygame.display.flip()
    time.sleep(5) #time delay so user can see their answer

def drawGrid():
    #this draws the grid for the functions to be plotted

    #sets size and colour of screen
    windowSurface.set_clip(0,0,600,600)
    windowSurface.fill('white')

    for i in range(30): #iterates 30 times to draw lines across the screen
        xaxes = 20*i
        yaxes = 20*i
        pygame.draw.line(windowSurface, 'grey', (xaxes,0),(xaxes,600), 1) #sets colour, size of line and coordinates of horizontal lines that make the x axis
        pygame.draw.line(windowSurface, 'grey', (0,yaxes),(600,yaxes), 1) #sets colour, size of line and coordinates of vertical lines that make the y axis

    pygame.display.flip() #updates the screen

    #draws slightly thicker, black lines for the x and y axis in the through the middle of the screen vertically and horizontally
    pygame.draw.line(windowSurface, 'black', (300, 0), (300, 600), 3)
    pygame.draw.line(windowSurface, 'black',(0,300), (600, 300), 3)
    num = 0
    #this labels the axes with numbers
    for i in range(15):
        font = pygame.font.Font(None, 20)
        numberlabel = font.render(str(i),20,'black')
        num = num + 20 
        windowSurface.blit(numberlabel, (280+num,300))
        pygame.display.flip()
    num = 1
    for i in range(15):
        font = pygame.font.Font(None, 20)
        numberlabel = font.render(str(i),20,'black')
        num = num + 20 
        windowSurface.blit(numberlabel, (300,280+num))
        pygame.display.flip()
                           
    pygame.display.flip() 

def GraphFunction1(): #note each function has its own python function, this is because the screen is being updated by pygame, if i made this one function
    #the second function would simply overwrite the first
    fetchfunction = con.execute("""SELECT Function FROM Functions WHERE Function_Num = 1 limit 1""") #fetches function from database to be graphed
    functionlist = str(fetchfunction.fetchall()) #sql returns SELECT queries as lists
    function = functionlist[3:-4] # so they have to be indexed so only the function is returned
    fetchcolour1 = con.execute("""SELECT Colour FROM Colours WHERE Colour_Func_ID = 1 limit 1""") #fetches colour from database for the function
    colour1list = str(fetchcolour1.fetchall())
    colour1 = colour1list[3:-4]
    con.commit()
    for i in range(600): #iterates through each point to be plotted on the grid
        try: #essentially plots checks if each pixel is within the eval() function and plots it 
            x = (300-i)/float(20) #it then draws a line from pixel to pixel
            y = eval(function) #python's eval function works by having an x value defined which it then inputs into the function
            coord1 = (300+x*20, 300-y*20)

            newx = x = (300-(i+1))/float(20)
            newy = eval(function)
            coord2 = (300+newx*20, 300-newy*20)

            pygame.draw.line(windowSurface, colour1, coord1, coord2, 2)
            pygame.display.flip()
        except:
            pass #this is an exception for functions that dont go past 0, the eval function can stop at 0 (such as log(x) and exponential functions) and the graph will still be drawn
    yintercept(function, 1) #sends the function to have its y intercept calculated
    GraphFunction2() #moves onto function 2 to be graphed

def GraphFunction2(): #does same as above function but just for next function the user's inputted
    con = sqlite3.connect("GraphingCalc.db")
    fetchfunction = con.execute("""SELECT Function FROM Functions WHERE Function_Num = 2 limit 1""")
    functionlist = str(fetchfunction.fetchall())
    function = functionlist[3:-4]
    fetchcolour2 = con.execute("""SELECT Colour FROM Colours WHERE Colour_Func_ID = 2 limit 1""")
    colour2list = str(fetchcolour2.fetchall())
    colour2 = colour2list[3:-4]
    con.commit()
    con.close()

    for i in range(600):
        try:
            x = (300-i)/float(20)
            y = eval(function)
            coord1 = (300+x*20, 300-y*20)

            newx = x = (300-(i+1))/float(20)
            newy = eval(function)
            coord2 = (300+newx*20, 300-newy*20)

            pygame.draw.line(windowSurface, colour2, coord1, coord2, 2)
            pygame.display.flip()
        except:
            pass
    yintercept(function, 2)
    displayproperties() #the intercepts button is displayed within this function, which allows the user to see the y intercepts of their functions and the integral
                    

                
def clearscreen(): #this function is called when i need the screen clearing
    windowSurface.fill('white')
    pygame.display.flip()

def yintercept(function, funcnum):
    x=0
    try:
        yintercept = eval(function) #when x=0, which is where the y-intercept would be
        yintercept = round(yintercept, 2)
        con.execute("""INSERT INTO YIntercepts (Function_YInt_ID, YIntercept_Value) VALUES(?,?)""", [funcnum, yintercept]) #this is an sql query that inserts y-intercepts into the database
        con.commit()
    except: #some functions (like log) cannot be evaluated because log(0) cannot be evaluated, so this is an exception for those functions
        pass

class TrapeziumRule:
  def __init__(self, func, a, b): #this is in a try clause because the program can't integrate some functions
    # Save the function and bounds as instance variables
    self.func = func
    self.a = a
    self.b = b

  def calculate(self):
    if self.a > self.b: # Check if the lower bound is greater than the upper bound
      self.a, self.b = self.b, self.a # Swap the bounds if necessary

    # Define the trapezium rule function
    def f(x):
      return eval(self.func) # Evaluate the function at x
    try:
        n = 1000 # Define the number of subintervals
        h = (self.b-self.a)/n # Calculate the width of each subinterval
        s = 0.5*(f(self.a) + f(self.b)) # Initialize the sum with the endpoints

        for i in range(1, n): # Loop over the subintervals
          s += f(self.a + i*h) # Add the value of the function at the midpoint of the subinterval

        return s*h
    except:
        pass

def calculateintegrals(): #this takes the values from the functions and inputs it into the class defined above to find the integral
    qub1 = con.execute("""SELECT UB FROM Functions JOIN Integration WHERE Function_Num = 1 limit 1""")
    qfunc1 = con.execute("""SELECT Function FROM Functions WHERE Function_Num = 1""")
    qlb1 = con.execute("""SELECT LB FROM Functions JOIN Integration WHERE Function_Num = 1 limit 1""")

    qub2 = con.execute("""SELECT UB FROM Functions JOIN Integration WHERE Function_Num = 2 limit 2""")
    qfunc2 = con.execute("""SELECT Function FROM Functions WHERE Function_Num = 2""")
    qlb2 = con.execute("""SELECT LB FROM Functions JOIN Integration WHERE Function_Num = 2 limit 2""")

    ub1 = str(qub1.fetchall())             
    func1 = str(qfunc1.fetchall())
    lb1 = str(qlb1.fetchall())
    ub2 = str(qub2.fetchall())
    func2 = str(qfunc2.fetchall())
    lb2 = str(qlb2.fetchall())

    for var in ub1:
        if var in "(''[],)":
            ub1 = ub1.replace(var,'')

    for var in lb1:
        if var in "([]'',)":
            lb1 = lb1.replace(var,'')

    for var in ub2:
        if var in "([''],)":
            ub2 = ub2.replace(var,'')

    for var in func1:
        if var in "[],'":
            func1 = func1.replace(var,'')

    for var in func2:
        if var in "[],'":
            func2 = func2.replace(var,'')

    for var in lb2:
        if var in "([''],)":
            lb2 = lb2.replace(var,'')

    intergrator = TrapeziumRule(str(func1[1:-1]),float(lb1),float(ub1))
    integral1 = intergrator.calculate()
    intergrator = TrapeziumRule(str(func2[1:-1]),float(lb2[len(lb1)+1:]),float(ub2[len(ub1)+1:]))
    integral2 = intergrator.calculate()
    con.execute("""UPDATE Integration SET Integral = ? WHERE Integral_Func_ID = 1 """, [integral1])
    con.execute("""UPDATE Integration SET Integral = ? WHERE Integral_Func_ID = 2 """, [integral2])
    con.commit()
    
    

def displayproperties():
    font = pygame.font.Font(None, 35)
    q1 = con.execute("""SELECT YIntercept_Value FROM Functions JOIN YIntercepts WHERE Function_Num = 1""")
    q2 = con.execute("""SELECT Integral FROM Functions JOIN Integration WHERE Function_Num = 1 """)
    q3 = con.execute("""SELECT Integral FROM Functions JOIN Integration WHERE Function_Num = 2 """)
    yint1 = str(q1.fetchall())
    integ1 = str(q2.fetchall())
    integ2 = str(q3.fetchall())
    for var in yint1:
        if var in "[]":
            yint1 = yint1.replace(var,'')#again, fetchall returns a list, so i format the list so its just the parts i need

    for var in integ1:
        if var in "([],)":
            integ1 = integ1.replace(var,'')

    for var in integ2:
        if var in "([],)":
            integ2 = integ2.replace(var,'')

    yintbtn = pygame.Rect(0,0,165,30)
    integbtn = pygame.Rect(470,0,165,30)
    pygame.draw.rect(windowSurface,'purple',yintbtn)
    pygame.draw.rect(windowSurface,'purple',integbtn)
    yintbtnlabel = font.render("y-intercept(s)",20,'white')
    integratebtnlabel = font.render("integrate",20,'white')
    windowSurface.blit(yintbtnlabel, (1,0))
    windowSurface.blit(integratebtnlabel, (480,0))
    pygame.display.flip()

    while True: #event handling
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN: #if user selects y-intercepts button, display their y intercepts
                if yintbtn.collidepoint(event.pos):
                    font = pygame.font.Font(None, 15)
                    yintlabel = font.render(str(yint1), 20,'purple')
                    windowSurface.blit(yintlabel,(0,40))
                    pygame.display.flip()

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if integbtn.collidepoint(event.pos):
                    if integ1 == "0.0 0.0":
                        pass
                    else:
                        font = pygame.font.Font(None, 15)
                        integlabel = font.render(str(integ1), 15, 'purple')
                        windowSurface.blit(integlabel,(370,40))
                        pygame.display.flip()

Main() #starts the program

