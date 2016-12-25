#!/usr/bin/env python
import bluetooth
import re
import sys
import time
import os
import signal
import math
import select

berlin = 60
filestamp = str(int(time.time()))
ouifile = open("oui.txt","r").readlines()
table = []
white = '\033[1;37;48m'
neutral = '\033[0;37;48m'
red = '\033[1;31;48m'
green = '\033[1;32;48m' 
yellow = '\033[1;33;48m'
blue = '\033[1;34;48m'
purple = '\033[1;35;48m'
cyan = '\033[1;36;48m'

def signal_handler(signal,frame):
	print('Exiting...')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def get_oui(mac):
	macidlist = mac.split(':')
	macid = macidlist[0] + macidlist[1] + macidlist[2]
	macmanu = ""
	for ln in ouifile:
		if re.search(macid.upper(),ln):
			try:
				macmanu = ln.split('\t')[2].rstrip()
			except IndexError:
				macmanu = "Unknown"
	if macmanu == "":
		macmanu = "Unknown"
	return macmanu

def lookupclass(hex_string):
	    CoD = int(hex_string, 16)
	    classes = ['Miscellaneous', 'Computer', 'Phone', 'LAN/Network Access Point',
		       'Audio/Video', 'Peripheral', 'Imaging', 'Wearable', 'Toy',
		       'Health']
	    major_number = (CoD >> 8) & 0x1f
	    if major_number < len(classes):
		major = classes[major_number]
	    elif major_number == 31:
		major = 'Uncategorized'
	    else:
		major = 'Reserved'

	    minor_number = (CoD >> 2) & 0x3f
	    minor = None

	    if major_number == 1:
		classes = [
		    'Uncategorized', 'Desktop workstation', 'Server-class computer',
		    'Laptop', 'Handheld PC/PDA (clamshell)', 'Palm-size PC/PDA',
		    'Wearable computer (watch size)', 'Tablet']
		if minor_number < len(classes):
		    minor = classes[minor_number]
		else:
		    minor = 'reserved'

	    elif major_number == 2:
		classes = [
		    'Uncategorized', 'Cellular', 'Cordless', 'Smartphone',
		    'Wired modem or voice gateway', 'Common ISDN access']
		if minor_number < len(classes):
		    minor = classes[minor_number]
		else:
		    minor = 'reserved'

	    elif major_number == 3:
		minor_number >> 3
		classes = [
		    'Fully available', '1% to 17% utilized', '17% to 33% utilized',
		    '33% to 50% utilized', '50% to 67% utilized',
		    '67% to 83% utilized', '83% to 99% utilized',
		    'No service available']
		if minor_number < len(classes):
		    minor = classes[minor_number]
		else:
		    minor = 'reserved'

	    elif major_number == 4:
		classes = [
		    'Uncategorized', 'Wearable Headset Device', 'Hands-free Device',
		    '(Reserved)', 'Microphone', 'Loudspeaker', 'Headphones',
		    'Portable Audio', 'Car audio', 'Set-top box', 'HiFi Audio Device',
		    'VCR', 'Video Camera', 'Camcorder', 'Video Monitor',
		    'Video Display and Loudspeaker', 'Video Conferencing',
		    '(Reserved)', 'Gaming/Toy']
		if minor_number < len(classes):
		    minor = classes[minor_number]
		else:
		    minor = 'reserved'

	    elif major_number == 5:
		feel_number = minor_number >> 4
		classes = [
		    'Not Keyboard / Not Pointing Device', 'Keyboard',
		    'Pointing device', 'Combo keyboard/pointing device']
		feel = classes[feel_number]

		classes = [
		    'Uncategorized', 'Joystick', 'Gamepad', 'Remote control',
		    'Sensing device', 'Digitizer tablet', 'Card Reader', 'Digital Pen',
		    'Handheld scanner for bar-codes, RFID, etc.',
		    'Handheld gestural input device' ]
		if minor_number < len(classes):
		    minor_low = classes[minor_number]
		else:
		    minor_low = 'reserved'
		
		minor = '%s, %s' % (feel, minor_low)

	    elif major_number == 6:
		minors = []
		if minor_number & (1 << 2):
		    minors.append('Display')
		if minor_number & (1 << 3):
		    minors.append('Camera')
		if minor_number & (1 << 4):
		    minors.append('Scanner')
		if minor_number & (1 << 5):
		    minors.append('Printer')
		if len(minors > 0):
		    minors = ', '.join(minors)

	    elif major_number == 7:
		classes = ['Wristwatch', 'Pager', 'Jacket', 'Helmet', 'Glasses']
		if minor_number < len(classes):
		    minor = classes[minor_number]
		else:
		    minor = 'reserved'

	    elif major_number == 8:
		classes = ['Robot', 'Vehicle', 'Doll / Action figure', 'Controller',
		           'Game']
		if minor_number < len(classes):
		    minor = classes[minor_number]
		else:
		    minor = 'reserved'

	    elif major_number == 9:
		classes = [
		    'Undefined', 'Blood Pressure Monitor', 'Thermometer',
		    'Weighing Scale', 'Glucose Meter', 'Pulse Oximeter',
		    'Heart/Pulse Rate Monitor', 'Health Data Display', 'Step Counter',
		    'Body Composition Analyzer', 'Peak Flow Monitor',
		    'Medication Monitor', 'Knee Prosthesis', 'Ankle Prosthesis',
		    'Generic Health Manager', 'Personal Mobility Device']
		if minor_number < len(classes):
		    minor = classes[minor_number]
		else:
		    minor = 'reserved'

	    services = []
	    if CoD & (1 << 23):
		services.append('Information')
	    if CoD & (1 << 22):
		services.append('Telephony')
	    if CoD & (1 << 21):
		services.append('Audio')
	    if CoD & (1 << 20):
		services.append('Object Transfer')
	    if CoD & (1 << 19):
		services.append('Capturing')
	    if CoD & (1 << 18):
		services.append('Rendering')
	    if CoD & (1 << 17):
		services.append('Networking')
	    if CoD & (1 << 16):
		services.append('Positioning')
	    if CoD & (1 << 15):
		services.append('(reserved)')
	    if CoD & (1 << 14):
		services.append('(reserved)')
	    if CoD & (1 << 13):
		services.append('Limited Discoverable Mode')

	    output = [major]
	    if minor is not None:
		output.append(' (%s)' % minor)
	    output.append(': ')
	    output.append(', '.join(services))

	    return ''.join(output)


class MyDiscoverer(bluetooth.DeviceDiscoverer):
	def pre_inquiry(self):
		self.done = False

	def device_discovered(self,address,device_class,rssi,name):
		timestamp = int(time.time())
		result = (1.6 - (20 * math.log10(2440)) + math.fabs(rssi)) / 20
		meters = str(int(math.pow(10,result))) + "m"
		status = "yes"
		for i,line in enumerate(table):
			if line[0] == address:
				status = "no"
				table[i][1] = meters
				table[i][5] = timestamp
		if status == "yes":
			clhex = str(hex(device_class))
			desc = lookupclass(clhex)
			oui = get_oui(address)
			table.append([address,meters,name,oui,desc,timestamp])

	def inquiry_complete(self):
		self.done = True

def print_table(log):
	os.system('clear')
	now = int(time.time())
	for addr,meters,name,oui,desc,timestamp in table:
		lastseen = now - timestamp
		if lastseen <= berlin:
			print (white + "[" + addr + "]" + blue + " [+" + str(lastseen) + "s]" + green + " [" + meters + "]"+ yellow + " [" + name + "]" + purple + " [" + oui + "]" + cyan + " [" + desc + "]" + neutral)
	if log:
		logfile = open("bluescan-" + filestamp + ".log", "wb")
		for addr,meters,name,oui,desc,timestamp in table:
			logfile.write(addr + ";" + name + ";" + oui + ";" + desc + "\n")
			
	
d = MyDiscoverer()

while True:

	print "SCANNING..."
	d.find_devices(duration=5,lookup_names=True,flush_cache=True)

	readfiles = [ d, ]

	while True:
		rfds = select.select( readfiles, [], [] )[0]

		if d in rfds:
			d.process_event()

		if d.done:
			print_table(True)
			break
		
	time.sleep(5)













