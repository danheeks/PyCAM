; HeeksCAM, derived from HeeksCAD, has everything from HeeksCAD plus machining and simulation
#include "../PyCAD/HeeksCAD.iss"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{1ADA7A8A-6931-4810-9EF1-1BB8BD42A1E2}
AppName=Heeks CAM
AppVerName=Heeks CAM 2.0.1
DefaultDirName={pf}\HeeksCAM
DefaultGroupName=Heeks CAM
OutputBaseFilename=Heeks CAM 2.0.1

[Files]
Source: "C:\Dev\dsim\sim.pyd"; DestDir: "{app}\dsim"; Flags: ignoreversion
Source: "C:\Dev\dsim\SimApp.py"; DestDir: "{app}\dsim"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\dsim\Toolpath.py"; DestDir: "{app}\dsim"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\dsim\bitmaps\*.png"; DestDir: "{app}\dsim\bitmaps"; Flags: ignoreversion; Permissions: users-modify

Source: "C:\Dev\PyCAM\HeeksCAM.bat"; DestDir: "{app}\PyCAM"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\*.py"; DestDir: "{app}\PyCAM"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\*.pyd"; DestDir: "{app}\PyCAM"; Flags: ignoreversion
Source: "C:\Dev\PyCAM\*.png"; DestDir: "{app}\PyCAM"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\default.tooltable"; DestDir: "{app}\PyCAM"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\*.png"; DestDir: "{app}\PyCAM\bitmaps"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\depthop\*.png"; DestDir: "{app}\PyCAM\bitmaps\depthop"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\drilling\*.png"; DestDir: "{app}\PyCAM\bitmaps\drilling"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\pattern\*.png"; DestDir: "{app}\PyCAM\bitmaps\pattern"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\pocket\*.png"; DestDir: "{app}\PyCAM\bitmaps\pocket"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\profile\*.png"; DestDir: "{app}\PyCAM\bitmaps\profile"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\stock\*.png"; DestDir: "{app}\PyCAM\bitmaps\stock"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\serialnums\*.png"; DestDir: "{app}\PyCAM\bitmaps\serialnums"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\surface\*.png"; DestDir: "{app}\PyCAM\bitmaps\surface"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\bitmaps\tool\*.png"; DestDir: "{app}\PyCAM\bitmaps\tool"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\icons\*.png"; DestDir: "{app}\PyCAM\icons"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\nc\*.py"; DestDir: "{app}\PyCAM\nc"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\PyCAM\nc\machines.xml"; DestDir: "{app}\PyCAM\nc"; Flags: ignoreversion; Permissions: users-modify

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Heeks CAM"; Filename: "{app}\PyCAM\HeeksCAM.bat"; WorkingDir: "{app}\PyCAM"
Name: "{commondesktop}\Heeks CAM"; Filename: "{app}\PyCAM\HeeksCAM.bat"; WorkingDir: "{app}\PyCAM"; Tasks: desktopicon

