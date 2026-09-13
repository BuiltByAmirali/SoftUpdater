; ============================================================
;  SoftUpdater - official Windows installer (Inno Setup 6)
;
;  Compiled automatically by build_installer.bat:
;      ISCC /DAPP_VERSION=1.0.0 installer\SoftUpdater.iss
;  Output: dist\installer\SoftUpdater-Setup-<version>.exe
;
;  Free tool: https://jrsoftware.org/isinfo.php
; ============================================================

#ifndef APP_VERSION
  #define APP_VERSION "0.0.0"
#endif

#define MyAppName "SoftUpdater"
#define MyAppExeName "SoftUpdater.exe"
#define MyAppPublisher "BuiltByAmirali"
#define MyAppURL "https://github.com/BuiltByAmirali/SoftUpdater"

[Setup]
; Fixed GUID - never change it, or upgrades become "new software".
AppId={{CDDF3434-9D2C-41F8-84B1-C17F23C80325}
AppName={#MyAppName}
AppVersion={#APP_VERSION}
AppVerName={#MyAppName} {#APP_VERSION}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
; per-user install (no admin/UAC): {autopf} = user Programs folder
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=license_en.txt
SetupIconFile=..\app\assets\app.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
; CloseApplications=no ON PURPOSE: the stock "the following applications
; are using files that need to be updated by Setup" question (Windows
; Restart Manager) looked like an error to end users. A running
; SoftUpdater is instead closed silently by the [Code] section below,
; so Setup never stops to ask and never shows that dialog.
CloseApplications=no
OutputDir=..\dist\installer
OutputBaseFilename=SoftUpdater-Setup-{#APP_VERSION}
VersionInfoVersion={#APP_VERSION}
VersionInfoProductVersion={#APP_VERSION}
; ---- code signing (optional - the 'signed release' of Windows world) ----
; After buying a code signing certificate: install it in Windows, add a
; sign tool named 'signtool' in Inno Setup (Tools > Configure Sign Tools),
; then remove the leading ';' from the next line and rebuild.
;SignTool=signtool $p

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\build\app\SoftUpdater.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; \
    Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; \
    Description: "{cm:LaunchProgram,{#MyAppName}}"; \
    Flags: nowait postinstall skipifsilent
[Code]
// Close a running SoftUpdater instance quietly BEFORE Setup touches the
// files, and again before the uninstaller removes them. The first
// taskkill (without /F) asks the app's windows to close nicely; the
// /F call is the fallback for background instances. Both calls are
// harmless when the app is not running - taskkill just sets an error
// code that we deliberately ignore.
procedure CloseRunningApp;
var
  ResultCode: Integer;
begin
  Exec('taskkill.exe', '/IM SoftUpdater.exe /T', '', SW_HIDE,
    ewWaitUntilTerminated, ResultCode);
  Sleep(500);
  Exec('taskkill.exe', '/F /IM SoftUpdater.exe /T', '', SW_HIDE,
    ewWaitUntilTerminated, ResultCode);
  Sleep(500);
end;

// Called by Setup right before installation begins.
function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  CloseRunningApp;
end;

// Called by the uninstaller before it removes any file.
function InitializeUninstall(): Boolean;
begin
  Result := True;
  CloseRunningApp;
end;

// Called at the very end of uninstallation: wipe the app's per-user
// settings (QSettings stores them under HKCU\Software\SoftUpdater),
// so installing the app again after removing it starts 100% fresh -
// the first-run quick tour shows again, exactly as intended.
// The user's downloaded installers and logs are deliberately kept.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RegDeleteKeyIncludingSubkeys(HKEY_CURRENT_USER, 'Software\SoftUpdater');
end;
