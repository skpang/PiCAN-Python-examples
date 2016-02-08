#!/usr/bin/python3
#
## simple_obdii_coolant_temp_request.py
# 
# This python3 program logs all CAN messages to the sd card.
# For use with PiCAN boards on the Raspberry Pi
# http://skpang.co.uk/catalog/pican2-canbus-board-for-raspberry-pi-2-p-1475.html
#
# Make sure Python-CAN is installed first http://skpang.co.uk/blog/archives/1220
#
# 08-02-16 Padded request with 5 bytes of zeros
# 01-02-16 SK Pang
#

import RPi.GPIO as GPIO
import can
import time
import os
from threading import Thread


led = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led,GPIO.OUT)
GPIO.output(led,True)

ENGINE_COOLANT_TEMP = 0x05
ENGINE_RPM          = 0x0C
VEHICLE_SPEED       = 0x0D
MAF_SENSOR          = 0x10
O2_VOLTAGE          = 0x14
THROTTLE            = 0x11

PID_REQUEST         = 0x7DF
PID_REPLY           = 0x7E8

print('\n\rCAN Rx test')
print('Bring up CAN0....')
os.system("sudo /sbin/ip link set can0 up type can bitrate 500000")
time.sleep(0.1)	
print('Ready')
try:
	bus = can.interface.Bus(channel='can0', bustype='socketcan_native')
except OSError:
	print('Cannot find PiCAN board.')
	GPIO.output(led,False)
	exit()

def can_rx_task():
	while True:
		message = bus.recv()
		
		if message.arbitration_id == PID_REPLY and message.data[2] == ENGINE_COOLANT_TEMP:
			c = '{0:f} {1:x} {2:x} '.format(message.timestamp, message.arbitration_id, message.dlc)
			s=''
			for i in range(message.dlc ):
				s +=  '{0:x} '.format(message.data[i])
			temperature = message.data[3] - 40			#Convert data into temperature in degree C
	
			print('\r {}  Coolant temp = {} degree C  '.format(c+s,temperature))

t = Thread(target = can_rx_task)
t.start()

# Main loop
try:
	while True:
		GPIO.output(led,True)	

		# Sent a engine coolant temperature request
		msg = can.Message(arbitration_id=PID_REQUEST,data=[0x02,0x01,ENGINE_COOLANT_TEMP,0x00,0x00,0x00,0x00,0x00],extended_id=False)
		bus.send(msg)

		time.sleep(0.1)
		GPIO.output(led,False)
		time.sleep(0.1)	
 
	
except KeyboardInterrupt:
	#Catch keyboard interrupt
	GPIO.output(led,False)
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	
