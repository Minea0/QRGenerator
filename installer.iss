[Setup]
AppName=QRGenerator
AppVersion=1.0.1
DefaultDirName={pf}\QRGenerator
DefaultGroupName=QRGenerator
OutputDir=output
OutputBaseFilename=QRGeneratorSetup
SetupIconFile=logo.ico
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\QRGenerator.exe
AllowNoIcons=yes
DisableReadyMemo=no
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\QRGenerator\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\QRGenerator"; Filename: "{app}\QRGenerator.exe"
Name: "{commondesktop}\QRGenerator"; Filename: "{app}\QRGenerator.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; Flags: unchecked

[Run]
Filename: "{app}\QRGenerator.exe"; Description: "Launch QR Generator"; Flags: nowait postinstall skipifsilent

[Registry]
; Mark first-time install in HKCU
Root: HKCU; Subkey: "Software\QRGenerator"; ValueType: dword; ValueName: "Installed"; ValueData: 1; Flags: uninsdeletevalue

[Code]
function InitializeSetup(): Boolean;
var
  Installed: Cardinal;
begin
  // Check registry if already installed
  if RegQueryDWordValue(HKCU, 'Software\QRGenerator', 'Installed', Installed) then
  begin
    // Already installed -> run silently
    WizardForm.Hide;
    Result := True;
  end
  else
  begin
    // First-time install -> show wizard
    Result := True;
  end;
end;
