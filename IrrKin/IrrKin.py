# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 10:35:07 2024

@author: jorst136

Here: code that works with the IrrKin AutoHotKey script

"""
import tools.functions as Functions
        
def turnLED_ON():
    print("======= IrrKin =======")
    Functions.turnLED_ON()

def turnLED_OFF():
    print("======= IrrKin =======")
    Functions.turnLED_OFF()

def StopIrrKin():
    """ Exit just this IrrKin window """
    print(">>> Exiting IrrKin Mode")
    Functions.turnLED_OFF()

def closeEvent(event):
    """ Close event: associated with X button by default"""
    turnLED_OFF()
    print("=== closeEvent === Closing IrrKin window...")


