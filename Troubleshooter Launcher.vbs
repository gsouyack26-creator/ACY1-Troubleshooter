' ACY1 Troubleshooter - Auto-Update Launcher
' On every launch: copy the latest HTML from the share to a local cache, then open it.
' If the share is unreachable, opens the last cached local copy (offline-tolerant).
' Opens in Chrome if present, else Edge, else the system default browser.
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
    Dim browser
    browser = FindBrowser()
    If Len(browser) > 0 Then
        sh.Run """" & browser & """ """ & localFile & """", 1, False
    Else
        ' No Chrome/Edge found - hand off to the system default browser
        CreateObject("Shell.Application").ShellExecute localFile, "", "", "open", 1
    End If
Else
    MsgBox "Troubleshooter could not be found locally and the share drive is unreachable." & vbCrLf & _
           "Connect to the Amazon network and try again.", 48, "ACY1 Troubleshooter"
End If

' Return the first installed Chrome or Edge executable path, or "" if neither is found.
Function FindBrowser()
    Dim pf, pf86, lad, list, p
    pf   = sh.ExpandEnvironmentStrings("%ProgramFiles%")
    pf86 = sh.ExpandEnvironmentStrings("%ProgramFiles(x86)%")
    lad  = sh.ExpandEnvironmentStrings("%LocalAppData%")
    list = Array( _
        pf   & "\Google\Chrome\Application\chrome.exe", _
        pf86 & "\Google\Chrome\Application\chrome.exe", _
        lad  & "\Google\Chrome\Application\chrome.exe", _
        pf86 & "\Microsoft\Edge\Application\msedge.exe", _
        pf   & "\Microsoft\Edge\Application\msedge.exe" )
    FindBrowser = ""
    For Each p In list
        If fso.FileExists(p) Then
            FindBrowser = p
            Exit Function
        End If
    Next
End Function
