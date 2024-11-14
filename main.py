# -*- coding: utf-8 -*-
"""
Created on Wednesday July 17th 2024

Based on: https://www.hackster.io/ansh2919/serial-communication-between-python-and-arduino-e7cce0
Modified by: Jorn Steen

Interactive command-line script for communication with an Arduino
    in MOD Mode
Using the Adafruit MCP4725 breakout board for digital-to-analog (DAC) conversion

Operation:
- make sure that the correct script is uploaded to the Arduino
        (DAC_0to5V_v2.ino)
- execute this .py script in the PowerShell

GUI:
- Choose an LED -- the twelvebit_max gets adjusted from 4095 to the corrected 
    value according to the allowed maximum current of the LED

- IMPORTANT: The Current Limit on the LED Driver should be set to the max (1.2 A)
    
- Input a percentage using the slider
    -- this gets converted to a 12-bit string and sent to the Arduino

"""

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QComboBox,
 QSlider, QPushButton, QLabel, QMessageBox, QPlainTextEdit, QMainWindow, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal

import serial ## for communication with Arduino COM port
import time

import tools.constants as Constants
import tools.settings as Settings
import tools.functions as Functions # test version
import tools.IrrKin as IrrKin
# from tools.functions import write_read # test version


##############
Constants.MODE = "TEST" ##!!! TURN OFF WHEN NOT TESTING
##############

############## define Arduino write-read function ##############

MaxCurrents = Constants.MaxCurrents
##!!! CHECK CURRENTS

twelvebit_zero = Constants.twelvebit_zero
twelvebit_max_default = Constants.twelvebit_max_default
MaxCurrent_default = Constants.MaxCurrent_default

########################################################

def AdjustMaxCurrent(LED):
    MaxCurrent = MaxCurrents[LED]
    fraction = MaxCurrent / MaxCurrent_default
    twelvebit_max_thisLED = round(fraction * twelvebit_max_default)
    return MaxCurrent, twelvebit_max_thisLED

def percent_to_12bit(twelvebit_max, percent):
    fraction = percent / 100
    twelvebit_adj = twelvebit_max * fraction
    twelvebit_adj_round = round(twelvebit_adj)
    return twelvebit_adj_round

########################################################
######################### GUI ##########################
########################################################

class MainWindow(QMainWindow):
    # close_signal = pyqtSignal()
    
    def __init__(self):
        # super().__init__()
        super(MainWindow, self).__init__()
        uic.loadUi('UIs/MainWindow.ui', self)  # Load the UI file you provided

        #### Initialize instance variables ####
        self.selected_option = None
        self.percentage = 0 # start with 0%

        Settings.twelvebit_max_thisLED = None
        Settings.twelvebit_adjusted = None
        self.current = 0

################

        #### drop-down menu ####
        self.comboBox_LEDs.addItems(list(MaxCurrents.keys()))
        self.comboBox_LEDs.currentIndexChanged.connect(self.update_dropdown)

################

        #### Create textfield for Percentage ####
        self.textEdit_Percentage.setPlainText(str(self.percentage)) # 
        self.textEdit_Percentage.textChanged.connect(self.update_percentage)

        #### slide bar ####
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setValue(self.percentage)
        self.horizontalSlider.valueChanged.connect(self.update_slider)
        
################

        #### buttons ####        
        self.pushButton_LED_ON.clicked.connect(self.show_popup_ON)
        self.pushButton_LED_OFF.clicked.connect(self.turnLED_OFF)

        #### Save, Close and Continue button ####
        self.pushButton_SaveContinue.clicked.connect(self.SaveContinue)

        #### Cancel button ####
            ##!!! NEED TO FIX!!
        self.pushButton_Cancel.clicked.connect(self.cancel_gui)

################################################
################ INSTANCE VARIABLES ############
################################################
        
        self.initialise_Arduino(Constants.MODE)

        #### Initial calculation ####
        self.update_dropdown()
        self.turnLED_OFF() # extra caution
        
    def initialise_Arduino(self, MODE):
        """ Start COM port communication with Arduino (unless TEST MODE is on) """
        if MODE == "TEST":
            ### TEST ###
            pass
        elif MODE == "FORREAL":
            Settings.arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1) ## fibirr laptop
            # Settings.arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1) ## my laptop
            time.sleep(2) ## need to wait a bit after opening the communication
        else:
            print("wrong value for MODE")
################################################
################################################

    def update_slider(self):
        self.percentage = self.horizontalSlider.value()
        self.textEdit_Percentage.setPlainText(str(self.percentage)) # 
        self.update_calculation()

    def update_dropdown(self):
        self.selected_option = self.comboBox_LEDs.currentText()
        self.MaxCurrent, Settings.twelvebit_max_thisLED = AdjustMaxCurrent(self.selected_option) ## use currently selected LED
        self.update_label_MaxCurrent()

    def update_calculation(self):
        Settings.twelvebit_adjusted = str(percent_to_12bit(Settings.twelvebit_max_thisLED,int(self.percentage)))
        print(f"update_calculation twelvebit_adjusted: {Settings.twelvebit_adjusted}")
        self.current = round((int(self.percentage) / 100) * self.MaxCurrent)
        self.update_label_CurrentCurrent()

    def update_label_MaxCurrent(self):
        self.textEdit_MaxCurrent.setText(str(self.MaxCurrent))

    def update_label_CurrentCurrent(self):
        if self.current is None:
            self.current = ''
        self.textEdit_CurrentCurrent.setText(str(self.current))
        
    def update_percentage(self):
        if self.textEdit_Percentage.toPlainText() == '':
            self.current = ''
            Settings.twelvebit_adjusted = None
            self.update_label_CurrentCurrent()
        elif 0 <= int(self.textEdit_Percentage.toPlainText()) <= 100:
            self.percentage = int(self.textEdit_Percentage.toPlainText())  # Convert the input to an integer
            self.horizontalSlider.setValue(self.percentage)
            self.update_calculation()
        else:
            self.current = "Wrong Percentage"
            Settings.twelvebit_adjusted = None
            self.update_label_CurrentCurrent()

################

    def show_popup_ON(self):
        msg = QMessageBox()
        msg.setWindowTitle("Please Confirm")
        msg.setText("Are you sure you want to turn ON the LED?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.buttonClicked.connect(self.turnLED_ON)
    
        # retval = msg.exec_() # Execute the dialog and get the return value
        msg.exec_() # Execute the dialog
    
    def turnLED_ON(self, i):
        if i.text() == "&Yes":
            if Settings.twelvebit_adjusted is None:
                QMessageBox.warning(self, "Error", "Wrong input percentage")
                return
        
            print("======= MainWindow =======")
            print(f"turnLED_ON twelvebit_adjusted: {Settings.twelvebit_adjusted}")
            Functions.write_read(Settings.arduino, Settings.twelvebit_adjusted, Constants.MODE) ## send ON signal to Arduino (percentage-adjusted)
            print("Turned ON the LED") 
            self.textEdit_LEDstatus.setText("ON")
        else:
            Functions.write_read(Settings.arduino, "0", Constants.MODE) ## send OFF signal to Arduino
            print("Turned OFF the LED")
            self.textEdit_LEDstatus.setText("OFF")

    def turnLED_OFF(self):
        print("======= MainWindow =======")
        Functions.write_read(Settings.arduino, "0", Constants.MODE) ## send OFF signal to Arduino
        print("Turned OFF the LED")
        self.textEdit_LEDstatus.setText("OFF")

################

    def SaveContinue(self):
        """ Save, Close and Continue with IrrKin mode controlled by .ahk script """
        QMessageBox.warning(self, "Just so you know", "Saving values, closing GUI, and continuing with IrrKin")
        
        self.window = IrrKin.IrrKin() # load Class that includes loadUi
        self.window.show()

        # self.close_signal.emit()
        # self.close()

    # def cancel_gui(self):
    #     ## Cancel
    #     self.close()
    #     # event.accept()

##!!! FIX BUG: CRASH WHEN CLICKING CANCEL

    def cancel_gui(self):
        """ Cancel button """
        # Functions.write_read(Settings.arduino, "0", Constants.MODE) ## send OFF signal to Arduino
        # print("Turned OFF the LED")
        print("=== CANCEL BUTTON === Closing application...")
        
        ## just need to close the MainWindow         
        self.close()  # Close the window
        
        
        # app = QApplication(sys.argv)
        # app.quit()
        # sys.exit(app.exec_()) # or this way?
        # sys.exit() # or this way?




    # def closeEvent(self, event):
    #     ## upon clicking the X button
    #     self.cancel_gui()
    #     event.accept()

##!!! add code to close the programme upon clicking X (like Cancel)

    def closeEvent(self, event):
        """ Close event: associated with X button by default"""
        Functions.write_read(Settings.arduino, "0", Constants.MODE) ## send OFF signal to Arduino
        print("Turned OFF the LED")
        # self.close()  # Close the window
        print("=== X BUTTON === Closing application...")

################

if __name__ == '__main__':
    
    # app = QApplication(sys.argv)
    
    ## Check if there's a pre-existing QApplication instance 
    ## If there is, use it. If there isn't, create a new one.
    ## https://stackoverflow.com/questions/24041259/python-kernel-crashes-after-closing-an-pyqt4-gui-application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    ### Ensure that the app is deleted when we close it
    app.aboutToQuit.connect(app.deleteLater)

    ####        
    gui = MainWindow()
    gui.show()

    ####
    # app.quit()
    # app.exec_() # this way?
    sys.exit(app.exec_()) # or this way?
    ####
        
    ###################################

    # if MODE == "TEST":
    #     print("TEST mode: Script is done.")
    # elif MODE == "FORREAL":
    #     #### Now you can use gui.twelvebit_adjusted after the GUI is closed ####
    #     twelvebit_adjusted = gui.twelvebit_adjusted
    #     print("Script continues with IrrKin part.")
    #     #### Continue with the rest of the script using twelvebit_adjusted
    #     ################ START ON-OFF LOOP ################

    #     while True:
    #         command = input("Enter a command (on/off/stop/help): ").lower() ## makes all characters non-capitalised
    #         if command == "on":
    #             print("LED is on")
    #             write_read(self.arduino, Settings.twelvebit_adjusted) ## send ON signal to Arduino (percentage-adjusted)
    #         elif command == "off":
    #             print("LED is off")
    #             write_read(self.arduino, "0") ## send OFF signal to Arduino
    #         elif command == "stop":
    #             print("Turning off LED and stopping the program...")
    #             write_read(self.arduino, "0") ## send OFF signal to Arduino
    #             if MODE == "TEST":
    #                 pass
    #             elif MODE == "FORREAL":
    #                 self.arduino.close() ## close the serial port
    #             else:
    #                 print("something wrong with code here")
    #             break ## Exit the loop to stop the program
    #         elif command == "help":
    #             print("Available commands: on/off/stop/help")
    #         else:
    #             print("Invalid command. Type 'help' for a list of commands.")
    # else:
    #     print("something wrong with MODE")
    #     ################################################################################
