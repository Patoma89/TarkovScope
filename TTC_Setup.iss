; Script de instalador Inno Setup para TTC (Tactical Tarkov Companion) v1.3.1
[Setup]
AppId={{8E9A3F21-6C4D-4F18-9A1E-7C52B8D3E110}
AppName=TTC (Tactical Tarkov Companion)
AppVersion=1.3.1
AppVerName=TTC (Tactical Tarkov Companion) v1.3.1
AppPublisher=Patoma89
AppPublisherURL=https://github.com/Patoma89/TarkovScope
AppSupportURL=https://github.com/Patoma89/TarkovScope/issues
AppUpdatesURL=https://github.com/Patoma89/TarkovScope/releases
DefaultDirName={localappdata}\TTC
DefaultGroupName=TTC (Tactical Tarkov Companion)
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist_installer
OutputBaseFilename=TTC_Setup_v1.3.1
SetupIconFile=ttc.ico
UninstallDisplayIcon={app}\TTC.exe
Compression=lzma2/normal
SolidCompression=yes
WizardStyle=modern
AppMutex=TTC_TacticalTarkovCompanion_Mutex

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\TTC.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "ttc.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "cache\gear\*"; DestDir: "{app}\cache\gear"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\keys\*"; DestDir: "{app}\cache\keys"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\medical\*"; DestDir: "{app}\cache\medical"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\weapons\*"; DestDir: "{app}\cache\weapons"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\TTC (Tactical Tarkov Companion)"; Filename: "{app}\TTC.exe"; IconFilename: "{app}\ttc.ico"
Name: "{autodesktop}\TTC (Tactical Tarkov Companion)"; Filename: "{app}\TTC.exe"; IconFilename: "{app}\ttc.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\TTC.exe"; Description: "{cm:LaunchProgram,TTC (Tactical Tarkov Companion)}"; Flags: nowait postinstall skipifsilent
