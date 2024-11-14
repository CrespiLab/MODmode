/*
TEST
*/

SetTitleMatchMode 2 ; for ControlSend command

; Change directory to that of this .ahk script which also contains the necessary .py script
ScriptDir := A_ScriptDir
ControlSend("cd " A_ScriptDir "{Enter}",, "Windows PowerShell")

; ControlSend("python main.py{Enter}",, "Windows PowerShell")
