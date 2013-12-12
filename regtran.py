# (C) 2013 Andy McCormick, Ryan Schuster
# MIT license
# see LICENSE.txt for details

import serial
from time import sleep


# register transfer protocol implemented on top of an RS232 channel

# TODO:
# methods to reconfigure the serial channel
# left justify data before sending


class RegTran:
	CMD_READ = 'r'
	CMD_WRITE = 'w'
	ACK = 'k'
	NACK = '!'
	BURST = 32
	def __init__(self):
		self.channel = serial.Serial()
	def channelOpen(self, port, baud, timeout):
		if self.channel.isOpen():
			self.channel.close()
		self.channel.port = port
		self.channel.baudrate = baud
		self.channel.timeout = timeout
		self.channel.open()
		sleep(2)			# give it some time to start up (Arduino resets when the channel opens)
		self.channel.flushInput()	# don't know if these are necessary, just in case...
		self.channel.flushOutput()
		self.channel.readline()		# for some reason we can't read from the Arduino unless this happens
	def channelClose(self):
		self.channel.close()
	def reset(self):
		self.channel.close()
		self.channel.open()
		sleep(2)
		self.channel.flushInput()
		self.channel.flushOutput()
		self.channel.readline()
	def commandRead(self, reg):
		self.channel.write(RegTran.CMD_READ + reg)
		data = self.channel.read(self.BURST)
		if len(data) < self.BURST:
			self.channel.write(RegTran.NACK)
			print 'error: read: timeout'
		self.channel.write(RegTran.ACK)
		return data
	def commandWrite(self, reg, data):
		if (len(data) != self.BURST):
			print 'commandWrite: error: bad packet length, no data sent'
			return
		self.channel.write(RegTran.CMD_WRITE + reg + data)
		ack = self.channel.read()
		if len(ack) < 1:
			print 'commandWrite: error: ack timeout'
		elif ack == RegTran.NACK:
			print 'commandWrite: error: nacked'
		elif ack != RegTran.ACK:
			print 'commandWrite: error: bad ack'
		return
