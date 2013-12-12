#!/usr/bin/env python

# (C) 2013 Andy McCormick, Ryan Schuster
# MIT license
# see LICENSE.txt for details

import sys
from controlboard import *
from time import sleep
import serial


def handleCommand(command):
	words = command.split()
	if len(words) == 0:
		return True
	words[0] = words[0].lower()
	try:
		if words[0] == 'help':
			print
			print 'Commands:'
			print
			print 'close                - close the connection to the control board'
			print 'exit|quit            - leave this program forever'
			print 'help                 - obvious'
			print 'open (port) (baud)   - opens a connection to the control board'
			print 'poll                 - loop and grab lots of samples'
			print 'program (filename)   - write a HEX file to the sensor board'
			print 'reset control|sensor - reset the control or sensor board'
			print 'start                - start sampling the sensor'
			print 'state                - report the control board state'
			print 'stop                 - stop sampling the sensor'
			print
			print 'poll and program commands can be cancelled with Ctrl-C without'
			print 'also exiting the interactive command line'
			print
		elif words[0] == 'exit' or words[0] == 'quit':
			print 'Goodbye forever.'
			print
			return False
		elif words[0] == 'open':
			if len(words) != 3:
				print 'usage:'
				print 'open (port) (baud)'
				return True
			port = words[1]
			baud = int(words[2])
			print 'Openning "' + port + '" with baud rate', baud
			controlBoard.open(port, baud)
			print 'Ready.'
		elif words[0] == 'close':
			controlBoard.close()
			print 'Connection closed.'
		elif words[0] == 'reset':
			if len(words) == 2:
				words[1] = words[1].lower()
				if words[1] == 'control':
					print 'Resetting control board...'
					controlBoard.reset()
					print 'Ready.'
					return True
				elif words[1] == 'sensor':
					print 'Resetting sensor board...'
					controlBoard.resetSlave()
					print 'Ready.'
					return True
			print 'usage:'
			print 'reset control|sensor'
		elif words[0] == 'program':
			try:
				print 'Programming sensor board with "' + words[1] + '"...'
				controlBoard.pmodeStart()
				controlBoard.erase()
				controlBoard.writeHexFile(words[1])
				controlBoard.pmodeEnd()
				print 'Ready.'
			except KeyboardInterrupt:
				print
				print 'Cancelled.'
		elif words[0] == 'start':
			print 'Starting control board sampling.'
			controlBoard.sampleStart()
		elif words[0] == 'stop':
			print 'Stopping control board sampling.'
			controlBoard.sampleEnd()
		elif words[0] == 'state':
			print 'Current control board state: ' + controlBoard.getState()
		elif words[0] == 'poll':
			try:
				while True:
					data = controlBoard.readMotion()
					words = list();
					for i in range(3):
						low = ord(data[i * 2])
						high = ord(data[i * 2 + 1])
						d = high * 256 + low
						if d >= 32768:
							d = d - 65536
						words.append(d)
					print 'X accel:', words[0], 'Y accel:', words[1], 'Z accel:', words[2]
					sleep(.05)
			except KeyboardInterrupt:
				print
				print 'Cancelled.'
		else:
			print 'Unknown command: "' + command + '"'
		return True
	except serial.serialutil.SerialException:
		print 'Serial port error.'
		return True

printUsage = False
portGiven = False
baudGiven = False
commandGiven = False
baud = 19200

i = 1
while i < len(sys.argv):
	param = sys.argv[i]
	if param == '-p':
		i = i + 1
		if i >= len(sys.argv):
			printUsage = True
			break;
		port = sys.argv[i]
		portGiven = True
	elif param == '-b':
		i = i + 1
		if i >= len(sys.argv):
			printUsage = True
			break;
		baud = sys.argv[i]
		baudGiven = True
	elif param == '-c':
		i = i + 1
		if i >= len(sys.argv):
			printUsage = True
			break;
		command = sys.argv[i]
		commandGiven = True
	else:
		printUsage = True
	i = i + 1


if printUsage:
	print
	print 'usage:'
	print sys.argv[0], '-p (port) [-b (baud)] [-c "command"]'
	print
	print '-p (port)    - specifies the system name of the RS232 port to use'
	print '-b (baud)    - specifies the baud rate of the serial connection'
	print '               default is 19200'
	print '-c "command" - executes "command" and quits, rather than entering'
	print '               the interactive terminal - useful for programming'
	print '               the sensor board'
	print
	sys.exit(1)


print
print 'AzInc Control Board Host Interface'
print
print '(C) 2013 Andy McCormick, Ryan Schuster'
print 'MIT license, no warranty'
print 'See LICENSE.txt for details.'
print

controlBoard = ControlBoard()
if portGiven:
	print 'Openning channel to control board...'
	controlBoard.open(port, baud)
	print 'Ready.'

if commandGiven:
	handleCommand(command)
else:
	while True:
		command = raw_input('>')
		if not handleCommand(command):
			break;

controlBoard.close()
