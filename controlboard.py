# (C) 2013 Andy McCormick, Ryan Schuster
# MIT license
# see LICENSE.txt for details

import regtran

# control board interface module

# TODO:
# factor out HEX file parsing to a separate module

def wordToByteString(word):
	return eval('"\\x' + hex(word & 0xff)[2:].rjust(2, '0') + '\\x' + hex((word & 0xff00) >> 8)[2:].rjust(2, '0') + '"')

class ControlBoard:
	REG_STATE = 's'
	REG_ADDRESS = 'a'
	REG_FLASH = 'p'
	REG_EEPROM = 'e'
	REG_TEST = 't'
	REG_MOTION = 'm'
	def __init__(self):
		self.regtran = regtran.RegTran()
	def open(self, port, baud):
		self.regtran.channelOpen(port, baud, 2)
	def close(self):
		self.regtran.channelClose()
	def reset(self):
		self.regtran.reset()
	def protocolTest(self):
		return self.regtran.commandRead(ControlBoard.REG_TEST)
	def getState(self):
		return self.regtran.commandRead(ControlBoard.REG_STATE)
	def pmodeStart(self):
		self.regtran.commandWrite(ControlBoard.REG_STATE, 'program'.ljust(32))
	def pmodeEnd(self):
		self.regtran.commandWrite(ControlBoard.REG_STATE, 'idle'.ljust(32))
	def sampleStart(self):
		self.regtran.commandWrite(ControlBoard.REG_STATE, 'sample'.ljust(32))
	def sampleEnd(self):
		self.regtran.commandWrite(ControlBoard.REG_STATE, 'idle'.ljust(32))
	def resetSlave(self):
		self.regtran.commandWrite(ControlBoard.REG_STATE, 'reset'.ljust(32));
	def erase(self):
		self.regtran.commandWrite(ControlBoard.REG_STATE, 'erase'.ljust(32))
	def writeEeprom(self, address, data):
		self.regtran.commandWrite(ControlBoard.REG_ADDRESS, wordToByteString(address).ljust(32))
		self.regtran.commandWrite(ControlBoard.REG_EEPROM, data)
	def readEeprom(self, address):
		self.regtran.commandWrite(ControlBoard.REG_ADDRESS, wordToByteString(address).ljust(32))
		return self.regtran.commandRead(ControlBoard.REG_EEPROM)
	def parseHexLine(self, line):
		line = line.rstrip()
		if len(line) < 11:
			print "invalid HEX line (too short)"
			return False
		if line[0] != ':':
			print "invalid HEX line (no start colon)"
			return False
		byteCount = int(line[1:3], 16)
		if len(line) != 2 * byteCount + 11:
			print "invalid HEX line (byte count mismatch, found ", len(line), " expected ", 2 * byteCount + 11, ")"
			return False
		address = int(line[3:7], 16)
		addressString = '"\\x' + line[5:7] + '\\x' + line[3:5] + '"'
		# TODO: check address
		recordType = int(line[7:9], 16)
		dataString = '"'
		for i in range(byteCount):
			dataString = dataString + '\\x' + line[9 + i * 2 : 11 + i * 2]
		dataString = dataString + '"'
		data = eval(dataString)
		checksum = int(line[9 + byteCount * 2 : 11 + byteCount * 2], 16)
		# TODO: check checksum
		if recordType == 0:
			return (address >> 1, data)
		elif recordType == 1:
			return False
		else:
			print "invalid HEX line (bad record type: ", recordType, ")"
			return False
	def writeHexFile(self, filename):
		f = open(filename, 'r')
		parsed = list();
		for line in f:
			new = self.parseHexLine(line)
			if new != False:
				parsed.append(new)
		pages = dict();
		for line in parsed:
			key = line[0] & 0xfff0
			if pages.has_key(key):
				if line[0] & 0x0f:
					pages[key] = pages[key] + line[1]
				else:
					pages[key] = line[1] + pages[key]
			else:
				if line[0] & 0x0f:
					pages[key] = line[1]
				else:
					pages[key] = line[1]
		for key in pages:
			addrStr = '"\\x' + hex(key & 0xff)[2:].rjust(2, '0') + '\\x' + hex((key & 0xff00) >> 8)[2:].rjust(2, '0') + '"'
			self.regtran.commandWrite(ControlBoard.REG_ADDRESS, eval(addrStr).ljust(32, '\0'))
			self.regtran.commandWrite(ControlBoard.REG_FLASH, pages[key].ljust(32, '\0'))
	def readMotion(self):
		return self.regtran.commandRead(ControlBoard.REG_MOTION)
