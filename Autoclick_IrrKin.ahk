﻿/*
====== MOD mode =====
TO DO:
[] Have this .ahk script start PowerShell


IMPORTANT:
> Make sure that the Arduino code is uploaded to the Arduino:
"ArduinoCode_DAC-0to5V.ino" (in the folder of the same name)
> Make sure that Windows Powershell is running
> Make sure that the python script "main.py" is in the same folder as your current working folder in Powershell
=====================
*/

SetTitleMatchMode 2 ; for ControlSend command
CoordMode "Mouse", "Client" ; set CoordMode to active window's client area

;Mode := "TEST"
Mode := "FORREAL"

if (Mode = "TEST")
{
	MeasurementWindow_Name := "TestWindow.txt - C:\Users\jorst136\Documents\Postdoc\GitHub\MODmode\Test - Geany (new instance)"
	MeasurementWindow_Coords := "x64 y44"
}
else if (Mode = "FORREAL")
{
	MeasurementWindow_Name := "AvaSoft 8"
	MeasurementWindow_Coords := "x141 y128"
}
else
{
	MsgBox("Something wrong with Mode")
	ExitApp
}

; Change directory to that of this .ahk script which also contains the necessary .py script
ControlSend("cd " A_ScriptDir "{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")

Delay_1 := 400 ; variable (ms) for delay between measurement and LED on
Delay_2 := 1300 ; variable (ms) for delay between LED off and measurement
Delay_12 := Delay_1 + Delay_2

; Start python script: python .\main.py
ControlSend("python main.py{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")

; MsgBox Please enter a name and location for the log file.
FileName := FileSelect("S24", , "Create a new log file", "CSV Document (*.csv)")
if FileName = ""
{
    MsgBox("The dialog was canceled.")
    ControlSend("stop{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")
    ExitApp
}
else
{
    FileObj := FileOpen(FileName ".csv","a") ; a=append
	FileObj.Write("Cycle,CurrentTime (YYYYMMDDHHMISS),ElapsedTime (s),Event`r`n")
    MsgBox("The following file was created:`n" FileName ".csv")
}

; add textbox to include parameters (below data) such as temperature

MyGui := Gui(,"Input")
MyGui.Add("Text",,"Interval (s):")
MyGui.AddEdit("vInterval_sec")
MyGui.Add("Text",,"Number of cycles:")
MyGui.AddEdit("vNumberofcycles")
MyGui.Add("Button","default w80","OK").OnEvent("Click", ProcessUserInput)
MyGui.OnEvent("Close", UserClose) ; when app is closed, UserClose() is activated
MyGui.OnEvent("Escape", UserClose) ; when Escape is pressed, Userclose() is activated
MyGui.Show()
return

ProcessUserInput(*)
{
	global ; assign all variables in function to be global
	Saved := MyGui.Submit() ; local object not visible outside of function
	Interval_ms := Saved.Interval_sec * 1000 ; n*1000 ms ; 
	Numberofcycles := Saved.Numberofcycles
	Measurementtime_sec := Saved.Numberofcycles * Saved.Interval_sec ; measurement time in seconds
	Measurementtime_min := Measurementtime_sec / 60 ; measurement time in minutes
	MsgBox("You entered " Saved.Interval_sec " sec intervals and " Saved.Numberofcycles " cycles. `r`n This will take " Measurementtime_sec " seconds (" Measurementtime_min " minutes). `r`n Press LCtrl+LAlt+. to start measurement.`r`n Stop script with hotkey: LAlt+, (any time while it's running)")
}


UserClose(*) ; close app without saving
{
FileObj.Close()

ControlSend("stop{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")

MsgBox("Closed the programme and turned off LED (please check).")
ExitApp
}

<!,:: ; stop script with hotkey: LAlt+, (any time while it's running)
{
FileObj.Close()
Sleep (Delay_1) ; need some delay to make sure that no keys are pressed when the programme is writing "stop"
ControlSend("stop{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")
MsgBox("Stopped the programme and turned off LED (please check).")
ExitApp
}

<^<!.:: ; activate with hotkey: LCtrl+LAlt+.
{

StartTime := A_TickCount
ControlClick MeasurementWindow_Coords, MeasurementWindow_Name ; AvaSoft single-measurement button (unless in TEST mode)
ElapsedTime := (A_TickCount - StartTime)/1000 ; Time stamp in seconds
FileObj.Write(A_index  "," A_Now "," ElapsedTime ",Measure"  "`r`n")
Sleep (Delay_1) ; need some delay between measurement and LED on

Loop (Numberofcycles) ; 
{
	ControlSend("on{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")
	ElapsedTime := (A_TickCount - StartTime)/1000 ; Time stamp in seconds
	FileObj.Write(A_index  "," A_Now "," ElapsedTime ",LEDon"  "`r`n")
	
	Sleep (Interval_ms-Delay_12) ; time that LED is ON: dependent on the user-input interval
	
	ControlSend("off{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")
	ElapsedTime := (A_TickCount - StartTime)/1000 ; Time stamp in seconds
	FileObj.Write(A_index  "," A_Now "," ElapsedTime ",LEDoff"  "`r`n")
		
	Sleep (Delay_2) ; need some delay between LED off and measurement
	
	ControlClick MeasurementWindow_Coords, MeasurementWindow_Name ; AvaSoft single-measurement button (unless in TEST mode)
	ElapsedTime := (A_TickCount - StartTime)/1000 ; Time stamp in seconds
	FileObj.Write(A_index  "," A_Now "," ElapsedTime ",Measure"  "`r`n")
		
	Sleep (Delay_1) ; need some delay between measurement and LED on
}
FileObj.Close()
ControlSend("stop{Enter}","Windows.UI.Input.InputSite.WindowClass1", "Windows PowerShell")
MsgBox("Done!")
ExitApp
}

/*
- How to add a timer that runs while the loop is running?
- Make CurrentTime display also milliseconds
*/
