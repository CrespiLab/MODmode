# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 10:35:07 2024

@author: jorst136

Here: code that works with the IrrKin AutoHotKey script

"""

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import (QMainWindow)
# from PyQt5.QtCore import Qt, pyqtSignal

# import time
import tools.settings as Settings
import tools.functions as Functions
# import tools.constants as Constants

class IrrKin(QMainWindow):
    """Dialog class for IrrKin mode."""
    def __init__(self):
        super(IrrKin, self).__init__()
        uic.loadUi('UIs/IrrKin.ui', self)  # Load the UI file you provided
              
        self.pushButton_LED_ON.clicked.connect(self.turnLED_ON)
        self.pushButton_LED_OFF.clicked.connect(self.turnLED_OFF)
        self.pushButton_Cancel.clicked.connect(self.StopIrrKin)
        
        self.turnLED_OFF() # start with LED OFF
        
        while True:
                command = input("Enter a command (on/off/stop/help): ").lower() ## makes all characters non-capitalised
                if command == "on":
                    # print("LED is on")
                    # write_read(self.arduino, Settings.twelvebit_adjusted) ## send ON signal to Arduino (percentage-adjusted)
                    self.turnLED_ON()
                elif command == "off":
                    # print("LED is off")
                    # write_read(self.arduino, "0") ## send OFF signal to Arduino
                    self.turnLED_OFF()
                elif command == "stop":
                    # print("Turning off LED and stopping the program...")
                    # write_read(self.arduino, "0") ## send OFF signal to Arduino
                    # if MODE == "TEST":
                        # pass
                    # elif MODE == "FORREAL":
                        # self.arduino.close() ## close the serial port
                    self.StopIrrKin()
                    # else:
                        # print("something wrong with code here")
                    # break ## Exit the loop to stop the program
                elif command == "help":
                    print("Available commands: on/off/stop/help")
                else:
                    print("Invalid command. Type 'help' for a list of commands.")
        
    def update_label_LEDstatus2(self):
        self.textEdit_LEDstatus2.setText(Settings.LEDstatus)
        
    def turnLED_ON(self):
        print("======= IrrKin =======")
        Functions.turnLED_ON()
        self.update_label_LEDstatus2()

    def turnLED_OFF(self):
        print("======= IrrKin =======")
        Functions.turnLED_OFF()
        self.update_label_LEDstatus2()

    def StopIrrKin(self):
        """ Exit just this IrrKin window """
        print(">>> Exiting IrrKin Mode")
        self.close()

    def closeEvent(self, event):
        """ Close event: associated with X button by default"""
        self.turnLED_OFF()
        print("=== closeEvent === Closing IrrKin window...")


