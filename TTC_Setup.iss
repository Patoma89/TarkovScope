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
DisableDirPage=no
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
Source: "cache\avatars\*"; DestDir: "{app}\cache\avatars"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\gear\*"; DestDir: "{app}\cache\gear"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\keys\*"; DestDir: "{app}\cache\keys"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\maps\*"; DestDir: "{app}\cache\maps"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\medical\*"; DestDir: "{app}\cache\medical"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\story_chapters\*"; DestDir: "{app}\cache\story_chapters"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\thumbs\*"; DestDir: "{app}\cache\thumbs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\trader_stocks\*"; DestDir: "{app}\cache\trader_stocks"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\weapons\*"; DestDir: "{app}\cache\weapons"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\TTC (Tactical Tarkov Companion)"; Filename: "{app}\TTC.exe"; IconFilename: "{app}\ttc.ico"
Name: "{autodesktop}\TTC (Tactical Tarkov Companion)"; Filename: "{app}\TTC.exe"; IconFilename: "{app}\ttc.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\TTC.exe"; Description: "{cm:LaunchProgram,TTC (Tactical Tarkov Companion)}"; Flags: nowait postinstall skipifsilent

[Code]
function SetEnvironmentVariableNull(lpName: string; lpValue: LongWord): BOOL;
  external 'SetEnvironmentVariableW@kernel32.dll stdcall';

function InitializeSetup(): Boolean;
var
  TclVal: string;
  TkVal: string;
begin
  { Limpia variables internas heredadas cuando el instalador se lanza desde una versión anterior empaquetada con PyInstaller --onefile }
  SetEnvironmentVariableNull('_PYI_APPLICATION_HOME_DIR', 0);
  SetEnvironmentVariableNull('_PYI_ARCHIVE_FILE', 0);
  SetEnvironmentVariableNull('_PYI_PARENT_PROCESS_LEVEL', 0);
  SetEnvironmentVariableNull('_PYI_SPLASH_IPC', 0);
  SetEnvironmentVariableNull('_MEIPASS2', 0);
  SetEnvironmentVariableNull('_MEIPASS', 0);

  TclVal := Uppercase(GetEnv('TCL_LIBRARY'));
  if Pos('_MEI', TclVal) > 0 then
    SetEnvironmentVariableNull('TCL_LIBRARY', 0);

  TkVal := Uppercase(GetEnv('TK_LIBRARY'));
  if Pos('_MEI', TkVal) > 0 then
    SetEnvironmentVariableNull('TK_LIBRARY', 0);

  Result := True;
end;

function IsInsideTempPath(const DirPath: string): Boolean;
var
  UpperDir: string;
  TempEnv: string;
  TmpEnv: string;
begin
  UpperDir := Uppercase(AddBackslash(Trim(DirPath)));
  TempEnv := Uppercase(AddBackslash(Trim(GetEnv('TEMP'))));
  TmpEnv := Uppercase(AddBackslash(Trim(GetEnv('TMP'))));

  Result := (Pos('\APPDATA\LOCAL\TEMP\', UpperDir) > 0) or
            (Pos('\WINDOWS\TEMP\', UpperDir) > 0) or
            ((TempEnv <> '\') and (Pos(TempEnv, UpperDir) = 1)) or
            ((TmpEnv <> '\') and (Pos(TmpEnv, UpperDir) = 1));
end;

procedure InitializeWizard();
begin
  { Nunca reutilizar una ruta previa ubicada dentro de Temp; si ocurre, volver a LocalAppData\TTC }
  if IsInsideTempPath(WizardForm.DirEdit.Text) then
    WizardForm.DirEdit.Text := ExpandConstant('{localappdata}\TTC');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpSelectDir then
  begin
    if IsInsideTempPath(WizardDirValue) then
    begin
      MsgBox(
        'No se recomienda instalar TTC dentro de una carpeta temporal (Temp), porque Windows o un limpiador puede borrar la aplicación.' + #13#10#13#10 +
        'Por favor elegí otra carpeta (por ejemplo: ' + ExpandConstant('{localappdata}\TTC') + ').',
        mbError, MB_OK
      );
      Result := False;
    end;
  end;
end;
