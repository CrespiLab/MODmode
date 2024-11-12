# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:34:15 2024

@author: jorst136
Functions for MODmode programme
"""
import time

# if MODE == "TEST":
#     ### TEST ###
# def write_read_test(x):
#     print(f'twelvebit_adjusted: {x}')

# elif MODE == "FORREAL":
    ############# code to communicate with COM port #############
    ### make sure the COM port is the correct one that is connected to the Arduino

# arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1) ## fibirr laptop
# # arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1) ## my laptop

# time.sleep(2) ## need to wait a bit after opening the communication
def write_read(arduino, x, MODE):
    if MODE == "TEST":
        print(f'==== TEST MODE ====\ntwelvebit_adjusted: {x}')
    
    elif MODE == "FORREAL":

        arduino.write(bytes(x, 'utf-8'))
        time.sleep(0.05)
        data = arduino.readline()
     	# print(f"data:{data}")
        return data
    else:
        print("wrong value for MODE")

# else:
    # print("wrong value for MODE")