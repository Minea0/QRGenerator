; ----------------------------------------------------------
; Inno Setup installer for QRGenerator
; ----------------------------------------------------------

[Setup]
AppName=QRGenerator
AppVersion=1.0.0
DefaultDirName={pf}\QRGenerator
DefaultGroupName=QRGenerator
DisableProgramGroupPage=no
OutputDir=output
OutputBaseFilename=QRGenerator_Setup
SetupIconFile=logo.ico
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\QRGenerator.exe
AllowNoIcons=yes
DisableReadyMemo=no
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

; Optional: self-delete installer if checkbox is selected
AppendDefaultDirName=no

[Files]
Source: "dist\QRGenerator\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\QRGenerator"; Filename: "{app}\QRGenerator.exe"
Name: "{commondesktop}\QRGenerator"; Filename: "{app}\QRGenerator.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; Flags: unchecked

[Run]
Filename: "{app}\QRGenerator.exe"; Description: "Launch QR Generator"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
