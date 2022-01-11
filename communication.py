#!/usr/bin/env python3

# libraries
import threading
import queue
import socket
import serial
import RPi.GPIO as GPIO

# setup for pwm for lidar motor
lidar_pin = 12 # pin for the pwm signal output
lidar_frequency = 25 # frequency of the pwm signal
lidar_duty = 100 # dutycycle of the pwm signal
GPIO.setwarnings(False)	# disable warnings
GPIO.setmode(GPIO.BOARD) # set pin numbering system
GPIO.setup(lidar_pin,GPIO.OUT) # define pin as output
pi_pwm = GPIO.PWM(lidar_pin,lidar_frequency) # create PWM instance with frequency 25Hz
pi_pwm.start(0) # start up pwm with dutycycle 0

# queue for UART-Data
q = queue.Queue(maxsize=2)

# Threads
# get data from lidar-sensor
def get_lidar():
    while True:
        ser = serial.Serial('/dev/ttyS0') # UART-GPIO pins on Raspberry ttyAMA0
        s = bytes(ser.read(100)) # bytes(ser.read())
        ##----Verarbeitung lidardaten hier----##
        print('lidar', s)
        q.put(s)
        ser.close()

# get data from xbee antennas
#def get_xbee():
   # while True:
       # ser = serial.Serial('/dev/ttyUSB0') #fixed USB-Port because only one USB device
       # s = bytes(ser.read(22))
       # print('xbee', s)
        #q.put(s)
        #ser.close()

# put the data from lidar and xbee together and send it to the plc
def do_mixer(conn):
    while True:
        s = q.get()
        print('mixer', s)
        #conn.send(s)
        q.task_done()

# sent data form plc to xbee antenna
#def sent_xbee(conn)
#   while True:
#        s = conn.recv()
#        ser = serial.Serial('/dev/ttyUSB0')
#        ser.write(s)
#        print('xbee_s', s)
#        ser.close()

# pwm signal for lidar motor
#def do_pwm():
#    while True:
#        pi_pwm.ChangeDutyCycle(lidar_duty)
pi_pwm.ChangeDutyCycle(lidar_duty)
# put queue data together
q.join()

# connect socket for ethernet communication
ethconn = socket.socket()
#ethconn.connect(('10.36.37.21', 1234)) #IP-Adress of Raspi and Portnumber. Portnumber must be the same as in PLC programm

# make threads
#xbee_thread = threading.Thread(target=get_xbee, daemon=True)
lidar_thread = threading.Thread(target=get_lidar, daemon=True)
mixer_thread = threading.Thread(target=do_mixer, args=(ethconn,), daemon=True)
#plc_thread = threading.Thread(target=sent_xbee, args=(ethconn,), daemon=True)
#pwm_thread = threading.Thread(target=do_pwm, daemon=True)

# start threads
#xbee_thread.start()
lidar_thread.start()
mixer_thread.start()
#plc_thread.start()
#pwm_thread.start()

# put threads together
#xbee_thread.join()
lidar_thread.join()
mixer_thread.join()
#plc_thread.join()
#pwm_thread.join()

### important for future use ###
# when using 2 or more devices on the USB-Ports you have to find out which device is which...
# because the raspberry pi uses ttyUSBx (x = 0...3) depending on which device it finds first.