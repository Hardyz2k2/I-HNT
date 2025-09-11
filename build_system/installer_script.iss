; YOLO Mob Finder - Inno Setup Installation Script
; Creates a professional Windows installer for the application

#define MyAppName "YOLO Mob Finder"
#define MyAppVersion "1.0"
#define MyAppPublisher "Gaming Automation Tools"
#define MyAppURL "https://github.com/your-username/Mouse-Mover"
#define MyAppExeName "YOLO_Mob_Finder.exe"
#define MyAppDescription "AI-Powered Real-Time Mob Detection and Targeting"
#define ProjectRoot ".."

[Setup]
; Application information
AppId={{B8E9C8A0-8B8A-4C8A-8B8A-8B8A8B8A8B8A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright © 2024 {#MyAppPublisher}
AppComments={#MyAppDescription}

; Installation directory
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Privileges and compatibility
PrivilegesRequired=admin
MinVersion=6.1sp1
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Output settings
OutputDir=installer_output
OutputBaseFilename=YOLO_Mob_Finder_Installer_v{#MyAppVersion}
SetupIconFile=app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; License and info files
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALLATION_INFO.txt
InfoAfterFile=USAGE_INSTRUCTIONS.txt

; Uninstaller
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Modern installer appearance
WizardImageFile=installer_image.bmp
WizardSmallImageFile=installer_small.bmp
WindowVisible=no
ShowLanguageDialog=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminLoggedOn
Name: "contextmenu"; Description: "Add 'Start Mob Finder' to context menu"; GroupDescription: "Integration"; Flags: unchecked

[Files]
; Main executable (built from project root)
Source: "{#ProjectRoot}\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Documentation files
Source: "{#ProjectRoot}\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ProjectRoot}\PROJECT_STATUS.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ProjectRoot}\README_YOLO.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#ProjectRoot}\requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
; YOLO model (if exists)
Source: "{#ProjectRoot}\yolov8n.pt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; Additional resources from build_system
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "INSTALLATION_INFO.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "USAGE_INSTRUCTIONS.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Start menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app_icon.ico"; Comment: "{#MyAppDescription}"
Name: "{group}\{#MyAppName} README"; Filename: "{app}\README.md"; Comment: "Read application documentation"
Name: "{group}\YOLO Training Guide"; Filename: "{app}\README_YOLO.md"; Comment: "Learn how to train custom YOLO models"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\app_icon.ico"; Comment: "{#MyAppDescription}"

; Quick launch (optional, older Windows versions)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; IconFilename: "{app}\app_icon.ico"

[Registry]
; Add context menu entry (optional)
Root: HKCR; Subkey: "Directory\Background\shell\MobFinder"; ValueType: string; ValueName: ""; ValueData: "Start Mob Finder Here"; Tasks: contextmenu; Flags: uninsdeletekey
Root: HKCR; Subkey: "Directory\Background\shell\MobFinder\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"""; Tasks: contextmenu

; Application registry entries
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey

[Run]
; Options to run after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent unchecked
Filename: "{app}\README.md"; Description: "Open README (recommended for first-time users)"; Flags: nowait postinstall skipifsilent shellexec unchecked

[UninstallDelete]
; Clean up any created files
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"
Type: dirifempty; Name: "{app}"

[CustomMessages]
LaunchProgram=Launch %1 after installation
ReadDocumentation=Read documentation

[Code]
// Custom functions for installer

function InitializeSetup(): Boolean;
begin
  Result := True;
  
  // Check Windows version
  if GetWindowsVersion < $06010000 then begin
    MsgBox('This application requires Windows 7 Service Pack 1 or newer.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Check if 64-bit Windows
  if not IsWin64 then begin
    if MsgBox('This application is optimized for 64-bit Windows.' + #13#10 + 
              'Continue with installation on 32-bit system?', mbConfirmation, MB_YESNO) = IDNO then begin
      Result := False;
      Exit;
    end;
  end;
end;

procedure InitializeWizard();
begin
  // Custom welcome message
  WizardForm.WelcomeLabel2.Caption := 
    'This will install ' + '{#MyAppName}' + ' on your computer.' + #13#10#13#10 +
    '{#MyAppDescription}' + #13#10#13#10 +
    'The application uses AI-powered YOLO detection for real-time ' +
    'visual mob targeting in games with 30+ FPS performance.' + #13#10#13#10 +
    'Click Next to continue, or Cancel to exit Setup.';
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := False;
  
  // Skip license page if no license file exists
  if (PageID = wpLicense) and not FileExists(ExpandConstant('{src}\LICENSE.txt')) then
    Result := True;
    
  // Skip info pages if files don't exist
  if (PageID = wpInfoBefore) and not FileExists(ExpandConstant('{src}\INSTALLATION_INFO.txt')) then
    Result := True;
    
  if (PageID = wpInfoAfter) and not FileExists(ExpandConstant('{src}\USAGE_INSTRUCTIONS.txt')) then
    Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  case CurStep of
    ssInstall:
      begin
        // Actions before installation starts
        Log('Starting installation of ' + '{#MyAppName}');
      end;
    ssPostInstall:
      begin
        // Actions after installation completes
        Log('Installation of ' + '{#MyAppName}' + ' completed');
        
        // Set file permissions if needed
        // (PyInstaller executables usually don't need special permissions)
      end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  case CurUninstallStep of
    usUninstall:
      begin
        Log('Uninstalling ' + '{#MyAppName}');
      end;
    usPostUninstall:
      begin
        // Clean up any remaining user data
        Log('Uninstall of ' + '{#MyAppName}' + ' completed');
      end;
  end;
end;

// Function to check for required dependencies (optional)
function DependenciesInstalled(): Boolean;
begin
  Result := True;
  // Since we're using PyInstaller with all dependencies bundled,
  // we don't need to check for external dependencies
  // This function can be extended if needed
end;