' ACY1 Troubleshooter - Auto-Update Launcher
' On every launch: copy the latest HTML from the share to a local cache, then open it.
' If the share is unreachable, opens the last cached local copy (offline-tolerant).
Option Explicit
Dim fso, sh, localDir, localFile, shareFile
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

localDir  = sh.ExpandEnvironmentStrings("%USERPROFILE%") & "\Documents\ACY1 Troubleshooter"
localFile = localDir & "\ACY1_Troubleshooter.html"
shareFile = "\\ant\dept-na\ACY1\Support\RME\Troubleshooter\ACY1_Troubleshooter.html"

If Not fso.FolderExists(localDir) Then fso.CreateFolder(localDir)

' Refresh from share when reachable; ignore errors (offline / share down)
On Error Resume Next
If fso.FileExists(shareFile) Then fso.CopyFile shareFile, localFile, True
On Error GoTo 0

If fso.FileExists(localFile) Then
    sh.Run "chrome.exe """ & localFile & """", 1, False
Else
    MsgBox "Troubleshooter could not be found locally and the share drive is unreachable." & vbCrLf & _
           "Connect to the Amazon network and try again.", 48, "ACY1 Troubleshooter"
End If
