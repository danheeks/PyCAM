; HeeksCAM, derived from HeeksCAD, has everything from HeeksCAD plus machining and simulation

#ifndef NAMES_DEFINED
#define NAMES_DEFINED
#define APP_ID "1ADA7A8A-6931-4810-9EF1-1BB8BD42A1E2"
#define APP_SUB_NAME "Cam"
#define EXE_FOLDER "PyCAM"
#endif

#include "../PyCAD/HeeksCAD.iss"

[Files]
Source: "C:\Dev\dsim\sim.pyd"; DestDir: "{app}\dsim"; Flags: ignoreversion
Source: "C:\Dev\dsim\SimApp.py"; DestDir: "{app}\dsim"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\dsim\Toolpath.py"; DestDir: "{app}\dsim"; Flags: ignoreversion; Permissions: users-modify
Source: "C:\Dev\dsim\bitmaps\*.png"; DestDir: "{app}\dsim\bitmaps"; Flags: ignoreversion; Permissions: users-modify
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


