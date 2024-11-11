# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 10:35:07 2024

@author: jorst136

Here: code that works with the IrrKin AutoHotKey script

"""

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import (QDialog, QPlainTextEdit, QMainWindow)
from PyQt5.QtCore import Qt, pyqtSignal

# import time
import tools.settings as Settings
import tools.functions as Functions
import tools.constants as Constants

class IrrKin(QMainWindow):
    """Dialog class for IrrKin mode."""
    def __init__(self):
        # self.parent_window = parent
        super(IrrKin, self).__init__
        uic.loadUi('IrrKin.ui', self)  # Load the UI file you provided
        
        self.pushButton_LED_ON.clicked.connect(self.turnLED_ON)
        self.pushButton_LED_OFF.clicked.connect(self.turnLED_OFF)

        self.turnLED_OFF() # start with LED OFF

        
    def turnLED_ON(self):
        print(f"turnLED_ON twelvebit_adjusted: {Settings.twelvebit_adjusted}")
        Functions.write_read(Settings.arduino, Settings.twelvebit_adjusted, Constants.MODE) ## send ON signal to Arduino (percentage-adjusted)
        print("Turned ON the LED") 
        self.textEdit_LEDstatus.setText("ON")


    def turnLED_OFF(self):
        Functions.write_read(Settings.arduino, "0", Constants.MODE) ## send OFF signal to Arduino
        print("Turned OFF the LED")
        self.textEdit_LEDstatus.setText("OFF")


