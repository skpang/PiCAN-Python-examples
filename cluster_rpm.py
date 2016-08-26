#!/usr/bin/python3
#
## cluster_rpm.py
# 
# This python3 program sends out CAN data from the PiCAN2 board to a Mazda RX8 instrument cluster.
# For use with PiCAN boards on the Raspberry Pi
# http://skpang.co.uk/catalog/pican2-canbus-board-for-raspberry-pi-2-p-1475.html
#
# Make sure Python-CAN is installed first http://skpang.co.uk/blog/archives/1220
#
# 27-08-16 SK Pang
#
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

RPM_PID		=  0x201
#oil temp 0x420

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


# Main loop
try:
	while True:
		for rpm in range(0,130):
			GPIO.output(led,True)
		
			msg = can.Message(arbitration_id=RPM_PID,data=[rpm,0x00,0,0,0,0,0,0],extended_id=False)
			bus.send(msg)
			print(' {0:d}'.format(rpm))
			time.sleep(0.01)
			GPIO.output(led,False)
			time.sleep(0.04)	
 
	
except KeyboardInterrupt:
	#Catch keyboard interrupt
	GPIO.output(led,False)
	os.system("sudo /sbin/ip link set can0 down")
	print('\n\rKeyboard interrtupt')	
