[Setup]
AppName=LocaalNoteTaker
AppVersion=@note-taker_VERSION@
DefaultDirName={pf}\LocaalNoteTaker
DefaultGroupName=LocaalNoteTaker
OutputDir=.\dist
OutputBaseFilename=note-taker-setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\note-taker\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LocaalNoteTaker"; Filename: "{app}\note-taker.exe"

[Run]
Filename: "{app}\note-taker.exe"; Description: "Launch Locaal Note Taker"; Flags: nowait postinstall skipifsilent
