import curses
import MySQLdb
import psycopg2
import os
import subprocess
import sys
import time
import curses.textpad
from utils.view import *



class NCursesHandler:

	def __init__(self):


		self.stdscr = curses.initscr() #initialize ncurses
		curses.noecho() # Disables automatic echoing of key presses (prevents program from input each key twice)
		curses.cbreak() # Runs each key as it is pressed rather than waiting for the return key to pressed)
		curses.start_color() #allow colors
		self.stdscr.keypad(1) # Capture input from keypad allow to move around on menus

		#Create color pairs.
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
		curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
		curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)
		curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
		curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)

		self.h = curses.color_pair(1) #h is the coloring for a highlighted menu option
		self.n = curses.A_NORMAL #n is the coloring for a non highlighted menu option

	#Clears screen and outputs exit menu
	def exit_window(self, new_menu, old_menu):
		self.stdscr.clear
		self.processmenu(new_menu, old_menu)
	#end exit_window

	#closes program
	def exit_program(self):
		curses.endwin() #Terminating ncurses application
		self.stdscr.addstr(0,0, "IN exit program")
		time.sleep(15)
		sys.exit()
	#end exit_program

	#properly loads form, returns values entered
	def runform(self, form):

		fieldcount = len(form['fields'])# how many fields there are in the form
		optioncount = len(form['options'])# how many options there are

		pos=0
		oldpos=None
		x = None
		optionselect = 0
		results = []

		# Display all fields

		for index in range(fieldcount):
		
			if index < fieldcount:
				self.stdscr.addstr(5+index,20, "%s" % (form['fields'][index]['title']), self.n)
				index += 1

		self.stdscr.border(0)
		self.stdscr.addstr(2,35, form['title'], curses.A_STANDOUT) # Title for this menu
		self.stdscr.addstr(4,16, form['subtitle'], curses.A_BOLD) # Subtitle for this menu
		self.stdscr.addstr(28,23, "Created By: Casey Balza, Daryle Cooke, & Nick Jurczak", curses.color_pair(2))

		#display options			

		for index in range(optioncount):
			textstyle = self.n
	
			if pos==fieldcount:
				if optionselect==index:
					textstyle = self.h
			self.stdscr.addstr(5+5*fieldcount,20+(index*20), "%s" % (form['options'][index]['title']), textstyle)
		self.stdscr.refresh()

		for index in range(fieldcount):
			if form['fields'][index]['type'] == Dictionary.TEXT:
				win = curses.newwin(1,30,5+index,20+len(form['fields'][index]['title']))
				tb = curses.textpad.Textbox(win)
				text = None
				def check(input):
					if input == 13:
						tb.gather()
				tb.do_command(check)
				text = tb.edit()
				results.append(text)


	# This function displays the appropriate menu and returns the option selected
	def runmenu(self, menu, parent, start):

		# work out what text to display as the last menu option
		if parent is None:
			lastoption = 0 #display no lastoption
		elif parent == "No":
			lastoption = "No"
		else:
			lastoption = "Return to %s" % parent['title']

		optioncount = len(menu['options']) # how many options in this menu

		pos=0 #pos is the zero-based index of the hightlighted menu option. Every time runmenu is called, position 			  returns to 0, when runmenu ends the position is returned and tells the program what opt$
		oldpos=None # used to prevent the screen being redrawn every time
		x = None #control for while loop, let's you scroll through options until return key is pressed then returns 		     pos to program

		# Loop until return key is pressed
		while x !=ord('\n'):
			if pos != oldpos:
				oldpos = pos
				self.stdscr.border(0)
				self.stdscr.addstr(2,35, menu['title'], curses.A_STANDOUT) # Title for this menu
				self.stdscr.addstr(4,16, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu
				self.stdscr.addstr(28,23, "Created By: Casey Balza, Daryl Cooke, & Nickolas Jurczak", curses.color_pair(2))

				# Display all the menu items, showing the 'pos' item highlighted
				count = 0
				for index in range(optioncount):
					index += start
					textstyle = self.n

					if pos==count:
						textstyle = self.h
					if count < 7 and index < optioncount:
						self.stdscr.addstr(5+count,20, "%d - %s" % (count+1, menu['options'][index]['title']), textstyle)
						count += 1
	
					elif count == 7:
						self.stdscr.addstr(5+count,20, "%d - %s" % (count+1, "MORE"), textstyle)				
						count += 1

			
				# Now display Exit/Return at bottom of menu
				if lastoption != 0:
					textstyle = self.n

					if pos==count:
						textstyle = self.h
					self.stdscr.addstr(5+count,20, "%d - %s" % (count+1, lastoption), textstyle)
					self.stdscr.refresh()
					# finished updating screen

			x = self.stdscr.getch() # Gets user input

			# What is user input?
			max = 0
			if optioncount <= 8:
				max = ord(str(optioncount+1))
			else:
				max = ord('9')
			if x >= ord('1') and x <= max:
				pos = x - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
			elif x == 258: # down arrow
				if pos < count:
					pos += 1
				else: pos = 0
			elif x == 259: # up arrow
				if pos > 0:
					pos += -1
				else: pos = count
			elif x == 69: # if user entered 'E' (shift + e) from the .getch()
				pos = 69
				return pos
		# return index of the selected item
		if pos == 8 or pos == optioncount:
			return -1
		elif pos == 7:
			return -2
		else:
			pos += start

			return pos
	#end runmenu()


	# This function calls showmenu and then acts on the selected item
	def processmenu(self, menu, parent=-1):
		optioncount = len(menu['options'])
		exitmenu = False
		start = 0
		if parent==-1:
			parent = main_menu
		if menu['type'] == Dictionary.MENU:
			while not exitmenu: #Loop until the user exits the menu
				getin = self.runmenu(menu, parent, start)
				if getin == -1 or getin == optioncount:
					return str(parent)
				elif getin == 69: #if user input 'E' (shift + e) bring up exit menu
					self.stdscr.clear()
					saying = "No"
					self.exit_window(exit_menu, saying) #open exit window
					self.stdscr.clear()#Clear screen of exit menu if user did not exit
				elif getin == -2:
					start += 7
					self.stdscr.clear()
				elif menu['options'][getin]['type'] == Dictionary.COMMAND:
					curses.def_prog_mode()    # save curent curses environment
					self.stdscr.clear() #clears previous screen
					result = (menu['options'][getin]['command']) # Get command into variable
					return result#Call the command
					#stdscr.clear() #clears previous screen on key press and updates display based on pos
					#curses.reset_prog_mode()   # reset to 'current' curses environment
					#curses.curs_set(1)         # reset doesn't do this right
					#curses.curs_set(0)
				elif menu['options'][getin]['type'] == Dictionary.MENU:
					self.stdscr.clear() #clears previous screen on key press and updates display based on pos
					self.processmenu(menu['options'][getin], menu) # display the submenu
					self.stdscr.clear() #clears previous screen on key press and updates display based on pos
				elif menu['options'][getin]['type'] == Dictionary.EXITMENU:
		  			exitmenu = True
		else:
			self.runform(menu)
	#end processmenu()
	
	# Starts program with main menu
	def startmenu(self):
		return self.processmenu(main_menu, None)

	def testfun(self):
		self.stdscr.clear()
		self.stdscr.refresh()
		self.stdscr.addstr(2,2, "WORKING", curses.A_STANDOUT)
		self.stdscr.getch()
	#end testfun()

	def resetscreen(self):
		self.stdscr.clear()
		self.stdscr.refresh()
	#end resetscreen()
