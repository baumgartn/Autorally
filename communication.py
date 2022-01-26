
#!/usr/bin/env python3

# libraries
import threading
import queue
import socket
import serial
import struct
import binascii
from  rplidar import RPLidar

#Serial Port Names from Xbee and Lidar USB
# defined in udev rule 10 for finding the right USB port for the Lidar and the USB
PORT_LIDAR = '/dev/ttyUSB_LIDAR'
PORT_XBEE = '/dev/ttyUSB_XBEE'

#define lidar element to use the lidar sensor
lidar = RPLidar(PORT_LIDAR)
# queue for UART-Data from lidar and xbee
q = queue.Queue(maxsize=22)
data = []

### --- Threads for the multithreading --- ###

# get data from lidar-sensor
def get_lidar():
    print('lidar__')
    ##----Verarbeitung lidardaten hier----##
    for measurment in lidar.iter_measurments():
        if measurment[1] == 0:
            dist = 8000
        else:           
            dist = int(measurment[3]) 
        deg = int(measurment[2])
        #print('degrees ')
        #print(deg)
        #print('distance  ')
        #print(dist)
        #print(type(measurment[0]))
        s = struct.pack('>hh',deg,dist)     
        print('lidar', s)
        q.put(s)
 
# get data from xbee antennas
def get_xbee():
    while True:
        ser = serial.Serial(PORT_XBEE,baudrate = 9600) #fixed USB-Port because only one USB device
            
        s = bytes(ser.read(22))
        print('xbee', s)
        q.put(s)
        ser.close()

# put the data from lidar and xbee together and send it to the plc
def do_mixer(conn):
    while True:
        print('mixer__')
        s = q.get()
        print('mixer', s)
        #conn.send(s)
        #q.task_done()



# put queue data together
q.join()

# connect socket for ethernet communication
ethconn = socket.socket()
#ethconn.connect(('10.36.37.21', 4711)) #IP-Adress of Raspi and Portnumber. Portnumber must be the same as in PLC programm

# make threads
xbee_thread = threading.Thread(target=get_xbee, daemon=True)
lidar_thread = threading.Thread(target=get_lidar, daemon=True)
mixer_thread = threading.Thread(target=do_mixer, args=(ethconn,), daemon=True)
#plc_thread = threading.Thread(target=sent_xbee, args=(ethconn,), daemon=True)


# start threads
xbee_thread.start()
lidar_thread.start()
mixer_thread.start()
#plc_thread.start()


# put threads together
xbee_thread.join()
lidar_thread.join()
mixer_thread.join()
#plc_thread.join()




# sent data form plc to xbee antenna for the control panel which we can forget lol
#def sent_xbee(conn)
#   while True:
#        s = conn.recv()
#        ser = serial.Serial('/dev/ttyUSB0')
#        ser.write(s)
#        print('xbee_s', s)
#        ser.close()
