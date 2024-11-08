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

GUI VERSION 1:
- Choose an LED -- the twelvebit_max gets adjusted from 4095 to the corrected 
    value according to the allowed maximum current of the LED

- IMPORTANT: The Current Limit on the LED Driver should be set to the max (1.2 A)
    
- Input a percentage using the slider
    -- this gets converted to a 12-bit string and sent to the Arduino

"""

import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QComboBox,
 QSlider, QPushButton, QLabel, QMessageBox, QPlainTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal

import serial ## for communication with Arduino COM port
import time

import tools.parameters as Parameters


############## define Arduino write-read function ##############
MODE = Parameters.MODE

##############
# MODE = "TEST"
# MODE = "FORREAL"
##############

if MODE == "TEST":
    ### TEST ###
    def write_read(x):
        print(f'twelvebit_adjusted: {x}')
elif MODE == "FORREAL":
    ############# code to communicate with COM port #############
    ### make sure the COM port is the correct one that is connected to the Arduino

    arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1) ## fibirr laptop
    # arduino = serial.Serial(port='COM5', baudrate=115200, timeout=.1) ## my laptop

    time.sleep(2) ## need to wait a bit after opening the communication
    def write_read(x):
        arduino.write(bytes(x, 'utf-8'))
        time.sleep(0.05)
        data = arduino.readline()
     	# print(f"data:{data}")
        return data
else:
    print("wrong value for MODE")

########################################################
twelvebit_zero = 0
twelvebit_max_default = 4095

MaxCurrent_default = 1200

##!!! ADD MESSAGE: MAKE SURE CURRENT LIMIT KNOB IS SET TO MAX (1.2 V)

##!!! CHECK CURRENTS
MaxCurrents = {
	'280 nm': 500,
	'310 nm': 600,
   '340 nm': 600,
	'365 nm': 1200,
    '395 nm': 1200,
    '455 nm': 1000,
    '505 nm': 1000,
    '530 nm': 1000,
    '625 nm': 1000,
    '780 nm': 800,
    'Max: 1200 mA': 1200
    }

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

class SimpleGUI(QWidget):
    close_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        #### Initialize instance variables ####
        self.selected_option = None
        # self.slider_value = 0
        self.percentage = 0

        self.twelvebit_max_thisLED = None
        self.twelvebit_adjusted = None
        self.current = 0

        #### Set up the main window ####
        self.setWindowTitle('LED settings')
        self.setGeometry(100, 100, 300, 250)

        #### Create a layout ####
        layout = QVBoxLayout()

################

        #### Create a label for the drop-down menu ####
        label_menu = QLabel('Choose an LED:')
        layout.addWidget(label_menu)

        #### Create a drop-down menu ####
        self.dropdown = QComboBox()
        self.dropdown.addItems(list(MaxCurrents.keys()))        
        self.dropdown.currentIndexChanged.connect(self.update_dropdown)
        layout.addWidget(self.dropdown)

        #### Display the Maximum Current associated with the chosen LED  ####
        self.MaximumCurrent_label = QLabel('Maximum Current: ')
        layout.addWidget(self.MaximumCurrent_label)

        label_warning = QLabel('IMPORTANT: Max Current limit on the LED driver itself should be set to 1.2 V')
        layout.addWidget(label_warning)

################

        #### Create a label for the slide bar ####
        self.label_slider = QLabel('Percentage:')
        layout.addWidget(self.label_slider)
        
        #### Create textfield for Percentage ####
        self.textfield_percentage = QPlainTextEdit()
        self.textfield_percentage.setMaximumHeight(30)
        self.textfield_percentage.setMaximumWidth(75)
        self.textfield_percentage.setPlainText(str(self.percentage)) # 
        self.textfield_percentage.textChanged.connect(self.update_percentage)
        layout.addWidget(self.textfield_percentage)

        #### Create a slide bar ####
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(self.percentage)

        self.slider.valueChanged.connect(self.update_slider)
        layout.addWidget(self.slider)

################

        #### Create a label to display the calculation result ####
        self.result_label = QLabel('Current: ')
        layout.addWidget(self.result_label)

################

        #### Create buttons ####
        self.button_ON = QPushButton('Turn LED ON', self)
        self.button_ON.clicked.connect(self.show_popup_ON)
        layout.addWidget(self.button_ON)

        self.button_OFF = QPushButton('Turn LED OFF', self)
        self.button_OFF.clicked.connect(self.turnLED_OFF)
        layout.addWidget(self.button_OFF)

        #### Create a label to display the status of the LED ####
        self.LEDstatus_label = QLabel('LED status: OFF')
        layout.addWidget(self.LEDstatus_label)

        #### Create a Save, Close and Continue button ####
        self.close_button = QPushButton('Save, Close and Continue', self)
        self.close_button.clicked.connect(self.close_gui)
        layout.addWidget(self.close_button)

        #### Create a Cancel button ####
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.cancel_gui)
        layout.addWidget(self.cancel_button)

################

        #### Set the layout for the main window ####
        self.setLayout(layout)

################################################
################ INSTANCE VARIABLES ############
################################################
        
        #### Initial calculation ####
        self.update_dropdown()
        
################################################
################################################

    def update_slider(self):
        self.percentage = self.slider.value()
        self.textfield_percentage.setPlainText(str(self.percentage)) # 
        self.update_calculation()

    def update_dropdown(self):
        self.selected_option = self.dropdown.currentText()
        self.MaxCurrent, self.twelvebit_max_thisLED = AdjustMaxCurrent(self.selected_option) ## use currently selected LED
        self.update_label_MaxCurrent()

    def update_calculation(self):
        self.twelvebit_adjusted = str(percent_to_12bit(self.twelvebit_max_thisLED,int(self.percentage)))
        print(f"update_calculation twelvebit_adjusted: {self.twelvebit_adjusted}")
        
        self.current = round((int(self.percentage) / 100) * self.MaxCurrent)

        self.update_label_CurrentCurrent()

    def update_label_MaxCurrent(self):
        self.MaximumCurrent_label.setText(f'Maximum Current: {self.MaxCurrent} mA')

    def update_label_CurrentCurrent(self):
        if self.current is None:
            self.current = ''
        self.result_label.setText(f'Current: {self.current} mA')
        
        # self.twelvebitadjusted_label.setText(f'12bit string (adjusted): {self.twelvebit_adjusted}')

    def update_percentage(self):
        if self.textfield_percentage.toPlainText() == '':
            self.current = ''
            self.twelvebit_adjusted = None
            self.update_label_CurrentCurrent()
        elif 0 <= int(self.textfield_percentage.toPlainText()) <= 100:
            self.percentage = int(self.textfield_percentage.toPlainText())  # Convert the input to an integer
            self.slider.setValue(self.percentage)
            self.update_calculation()
        else:
            self.current = "Wrong Percentage"
            self.twelvebit_adjusted = None
            self.update_label_CurrentCurrent()

################

    def show_popup_ON(self):
        msg = QMessageBox()
        msg.setWindowTitle("Please Confirm")
        msg.setText("Are you sure you want to turn ON the LED?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.buttonClicked.connect(self.turnLED_ON)
    
        retval = msg.exec_() # Execute the dialog and get the return value
    
    def turnLED_ON(self, i):
        if i.text() == "&Yes":
            print(f"turnLED_ON twelvebit_adjusted: {self.twelvebit_adjusted}")
            write_read(self.twelvebit_adjusted) ## send ON signal to Arduino (percentage-adjusted)
            print("Turned ON the LED") 
            self.LEDstatus_label.setText(f"LED status: ON ({self.current} mA)")
        else:
            write_read("0") ## send OFF signal to Arduino
            print("Turned OFF the LED")
            self.LEDstatus_label.setText("LED status: OFF")

    def turnLED_OFF(self, i):
        write_read("0") ## send OFF signal to Arduino
        print("Turned OFF the LED")
        self.LEDstatus_label.setText("LED status: OFF")

################

    def close_gui(self):
        """ Save, Close and Continue """
        QMessageBox.warning(self, "Just so you know", "Saving values, closing GUI, and continuing with IrrKin")
        
        self.close_signal.emit()
        self.close()

    # def cancel_gui(self):
    #     ## Cancel
    #     self.close()
    #     # event.accept()

    def cancel_gui(self):
        """ Cancel button """
        write_read("0") ## send OFF signal to Arduino
        print("Turned OFF the LED")
        app = QApplication(sys.argv)
        print("Closing application...")
        app.quit()

    # def closeEvent(self, event):
    #     ## upon clicking the X button
    #     self.cancel_gui()
    #     event.accept()

##!!! add code to close the programme upon clicking X (like Cancel)

    # def closeEvent(self, event):
    #     ## Cancel button
    #     app = QApplication(sys.argv)
    #     print("Closing application...")
    #     app.quit()

################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    
    def on_close():
        # print(f"Final result: {gui.result}")
        # Use gui.result for further processing here
        app.quit()

    gui.close_signal.connect(on_close)
    gui.show()
    app.exec_()
        
    ###################################

    if MODE == "TEST":
        print("TEST mode: Script is done.")
    elif MODE == "FORREAL":
        #### Now you can use gui.twelvebit_adjusted after the GUI is closed ####
        twelvebit_adjusted = gui.twelvebit_adjusted
        print("Script continues with IrrKin part.")
        #### Continue with the rest of the script using twelvebit_adjusted
        ################ START ON-OFF LOOP ################

        while True:
            command = input("Enter a command (on/off/stop/help): ").lower() ## makes all characters non-capitalised
            if command == "on":
                print("LED is on")
                write_read(twelvebit_adjusted) ## send ON signal to Arduino (percentage-adjusted)
            elif command == "off":
                print("LED is off")
                write_read("0") ## send OFF signal to Arduino
            elif command == "stop":
                print("Turning off LED and stopping the program...")
                write_read("0") ## send OFF signal to Arduino
                if MODE == "TEST":
                    pass
                elif MODE == "FORREAL":
                    arduino.close() ## close the serial port
                else:
                    print("something wrong with code here")
                break ## Exit the loop to stop the program
            elif command == "help":
                print("Available commands: on/off/stop/help")
            else:
                print("Invalid command. Type 'help' for a list of commands.")
    else:
        print("something wrong with MODE")
        ################################################################################
