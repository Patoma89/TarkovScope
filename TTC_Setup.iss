; Script de instalador Inno Setup para TTC (Tactical Tarkov Companion) v1.4.0
[Setup]
AppId={{8E9A3F21-6C4D-4F18-9A1E-7C52B8D3E110}
AppName=TTC (Tactical Tarkov Companion)
AppVersion=1.4.0
AppVerName=TTC (Tactical Tarkov Companion) v1.4.0
AppPublisher=Patoma89
AppPublisherURL=https://github.com/Patoma89/TarkovScope
AppSupportURL=https://github.com/Patoma89/TarkovScope/issues
AppUpdatesURL=https://github.com/Patoma89/TarkovScope/releases
DefaultDirName={localappdata}\TTC
DefaultGroupName=TTC (Tactical Tarkov Companion)
DisableDirPage=no
DisableProgramGroupPage=yes
DirExistsWarning=no
CloseApplications=yes
CloseApplicationsFilter=TTC.exe
PrivilegesRequired=lowest
OutputDir=dist_installer
OutputBaseFilename=TTC_Setup_v1.4.0
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
Source: "cache\route_data\*"; DestDir: "{app}\cache\route_data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "cache\route_maps\*"; DestDir: "{app}\cache\route_maps"; Flags: ignoreversion recursesubdirs createallsubdirs
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

function ExtractExePath(const RawCmd: string): string;
var
  S: string;
  P: Integer;
begin
  S := Trim(RawCmd);
  if S = '' then
  begin
    Result := '';
    exit;
  end;
  if Copy(S, 1, 1) = '"' then
  begin
    Delete(S, 1, 1);
    P := Pos('"', S);
    if P > 0 then
      S := Copy(S, 1, P - 1);
  end
  else
  begin
    P := Pos(' /', S);
    if P > 0 then
      S := Copy(S, 1, P - 1);
  end;
  Result := Trim(S);
end;

function NormDir(const DirPath: string): string;
begin
  Result := Uppercase(RemoveBackslashUnlessRoot(Trim(DirPath)));
end;

function ReadUninstallEntry(const RootKey: Integer; out UninstExe: string; out InstallLoc: string): Boolean;
var
  SubKey: string;
  RawUninst: string;
begin
  Result := False;
  UninstExe := '';
  InstallLoc := '';
  SubKey := 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{8E9A3F21-6C4D-4F18-9A1E-7C52B8D3E110}_is1';
  if not RegKeyExists(RootKey, SubKey) then
    exit;
  if not RegQueryStringValue(RootKey, SubKey, 'UninstallString', RawUninst) then
    RegQueryStringValue(RootKey, SubKey, 'QuietUninstallString', RawUninst);
  UninstExe := ExtractExePath(RawUninst);
  RegQueryStringValue(RootKey, SubKey, 'InstallLocation', InstallLoc);
  if InstallLoc = '' then
    RegQueryStringValue(RootKey, SubKey, 'Inno Setup: App Path', InstallLoc);
  if (InstallLoc = '') and (UninstExe <> '') then
    InstallLoc := ExtractFileDir(UninstExe);
  Result := (UninstExe <> '') and FileExists(UninstExe);
end;

procedure PreserveUserDatabaseIfNeeded(const OldDir: string; const NewDir: string);
var
  OldDb: string;
  NewDb: string;
begin
  if (OldDir = '') or (NewDir = '') or (NormDir(OldDir) = NormDir(NewDir)) then
    exit;
  OldDb := AddBackslash(OldDir) + 'data\tarkov_data.db';
  NewDb := AddBackslash(NewDir) + 'data\tarkov_data.db';
  if FileExists(OldDb) and (not FileExists(NewDb)) then
  begin
    ForceDirectories(AddBackslash(NewDir) + 'data');
    FileCopy(OldDb, NewDb, False);
  end;
end;

procedure UninstallPriorEntry(const RootKey: Integer; const RequireAdmin: Boolean; const TargetDir: string);
var
  UninstExe: string;
  OldDir: string;
  ResultCode: Integer;
begin
  if not ReadUninstallEntry(RootKey, UninstExe, OldDir) then
    exit;
  { Si está en HKCU en exactamente la misma carpeta, Inno Setup actualiza in-place sin desinstalar primero }
  if (not RequireAdmin) and (NormDir(OldDir) = NormDir(TargetDir)) then
    exit;

  PreserveUserDatabaseIfNeeded(OldDir, TargetDir);

  if RequireAdmin then
    ShellExec('runas', UninstExe, '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, ResultCode)
  else
    Exec(UninstExe, '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

function PrepareToInstall(var NeedsRestart: Boolean): string;
var
  TargetDir: string;
  ResultCode: Integer;
begin
  Result := '';
  TargetDir := WizardDirValue;

  { Cerrar cualquier instancia previa en ejecución para poder reemplazar TTC.exe sin bloqueos }
  Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM TTC.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Sleep(250);

  { Eliminar versiones previas registradas en HKLM (32/64 bits) o en otra carpeta de HKCU para evitar duplicados }
  if IsWin64 then
    UninstallPriorEntry(HKLM64, True, TargetDir);
  UninstallPriorEntry(HKLM32, True, TargetDir);
  UninstallPriorEntry(HKCU, False, TargetDir);
end;
