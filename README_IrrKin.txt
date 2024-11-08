=============================================================
INSTRUCTIONS for Autoclick_IrrKin_GUI.ahk
- This AutoHotkey script runs a kinetic measurement using AvaSoft
	- With LED irradiation
=============================================================
===========
IMPORTANT:
===========
> Make sure that the Arduino code is uploaded to the Arduino:
	"Serial_read_LED_loop_log.ino"
	-(in the folder of the same name)
	- It should be uploaded already, but upload it again using the Arduino IDE in case something went wrong.

> Make sure that Windows Powershell is running

> Make sure that the python script "interactive_v3.py" is in the same folder as your current working folder in Powershell
	- for example: set Powershell directory to that containing this Autoclick script
	- cd "workingfolder"

> AvaSoft: set it up for doing "Single measurement" (under the "Start" button)

> For AUTO-SAVE: in AvaSoft, configure "Live Output -- To File" in the tab "File": 
	- add an output and choose the location of your working folder (don't forget to press the Save button)
	- this will make sure your single spectra each get saved as an .Abs file
=============================================================
=============================================================
TO TURN OFF THE LED
(in case the AutoHotkey script got interrupted/cancelled and the LED was not off at that point)
===========
Write in the Windows PowerShell (copy-paste these three lines one after the other)
	- (you may need to close the PowerShell and open it again)
===========
$port = new-Object System.IO.Ports.SerialPort COM4,9600,None,8,one
$Port.Open()
$Port.WriteLine(0)
=============================================================
