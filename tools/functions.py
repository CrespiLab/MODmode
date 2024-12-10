# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:34:15 2024

@author: jorst136
Functions for MODmode programme
"""
import time
import tools.constants as Constants
import tools.settings as Settings
# import tools.IrrKin as IrrKin

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


def turnLED_ON():
    print(f"twelvebit_adjusted: {Settings.twelvebit_adjusted}")
    write_read(Settings.arduino, Settings.twelvebit_adjusted, Constants.MODE) ## send ON signal to Arduino (percentage-adjusted)
    print("Turned ON the LED") 
    Settings.LEDstatus = "ON"
        
def turnLED_OFF():
    write_read(Settings.arduino, "0", Constants.MODE) ## send OFF signal to Arduino
    print("Turned OFF the LED")
    Settings.LEDstatus = "OFF"
