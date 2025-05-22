
#define MyAppName "MPR Labs - MPR Separator"
#define MyAppVersion "1.0.3"
#define MyAppPublisher "MPR Labs"
#define MyAppURL "https://github.com/marcospr3421/MPRSeparator"
#define MyAppExeName "MPRSeparator.exe"

[Setup]
AppId={{8A69D345-D564-463C-AFF1-A69D9E530F96}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=MPRSeparator_Setup_v1.0.2
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CreateAppDir=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\version.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "setup_environment.py"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "{sys}\rundll32.exe"; Parameters: "sysdm.cpl,EditEnvironmentVariables"; Description: "Abrir configurações de variáveis de ambiente"; Flags: postinstall skipifsilent

[Dirs]
Name: "{localappdata}\{#MyAppName}\Data"; Permissions: users-full

[Code]
function EnvironVarExists(EnvVar: string): Boolean;
var
  Value: string;
begin
  Result := RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', EnvVar, Value);
end;

function GetDBServer(Param: String): String;
begin
  Result := DBServerEdit.Text;
end;

function GetDBName(Param: String): String;
begin
  Result := DBNameEdit.Text;
end;

function GetDBUsername(Param: String): String;
begin
  Result := DBUsernameEdit.Text;
end;

function GetDBPassword(Param: String): String;
begin
  Result := DBPasswordEdit.Text;
end;

function GetDBTable(Param: String): String;
begin
  Result := DBTableEdit.Text;
end;

function GetKeyVaultURI(Param: String): String;
begin
  Result := KeyVaultURIEdit.Text;
end;

function IsPythonInstalled(): Boolean;
var
  PythonPath: String;
begin
  PythonPath := GetPythonPath();
  Result := (PythonPath <> '');
end;

function GetPythonPath(): String;
var
  PythonExe: String;
  ResultCode: Integer;
  TempFile: String;
  TempFileHandle: Integer;
begin
  // Tentar encontrar python no PATH usando um arquivo temporário para capturar a saída
  TempFile := ExpandConstant('{tmp}\python_path.txt');
  
  if Exec(ExpandConstant('{cmd}'), '/c where python > "' + TempFile + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0) then
  begin
    if LoadStringFromFile(TempFile, PythonExe) then
    begin
      // Pegar apenas a primeira linha (primeiro Python encontrado)
      if Pos(#13#10, PythonExe) > 0 then
        PythonExe := Copy(PythonExe, 1, Pos(#13#10, PythonExe) - 1);
      if FileExists(PythonExe) then
      begin
        Result := Trim(PythonExe);
        DeleteFile(TempFile);
        Exit;
      end;
    end;
  end;
  DeleteFile(TempFile);

  // Verificar locais comuns de instalação
  if FileExists(ExpandConstant('{pf}\Python310\python.exe')) then
  begin
    Result := ExpandConstant('{pf}\Python310\python.exe');
    Exit;
  end;
  
  if FileExists(ExpandConstant('{pf}\Python39\python.exe')) then
  begin
    Result := ExpandConstant('{pf}\Python39\python.exe');
    Exit;
  end;

  // Verificar no registro
  if RegQueryStringValue(HKEY_CURRENT_USER, 'Software\Python\PythonCore\3.10\InstallPath', '', PythonExe) then
  begin
    Result := PythonExe + '\python.exe';
    Exit;
  end;

  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'Software\Python\PythonCore\3.10\InstallPath', '', PythonExe) then
  begin
    Result := PythonExe + '\python.exe';
    Exit;
  end;

  // Python não encontrado
  Result := '';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Notificar o sistema sobre a alteração nas variáveis de ambiente
    Exec(ExpandConstant('{sys}\rundll32.exe'), 'user32.dll,UpdatePerUserSystemParameters', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    
    // Executar o script de configuração do ambiente, se existir e se o Python estiver instalado
    if FileExists(ExpandConstant('{app}\setup_environment.py')) and IsPythonInstalled() then
    begin
      Exec(GetPythonPath(), ExpandConstant('"{app}\setup_environment.py"'), '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;

var
  DBConfigPage: TInputQueryWizardPage;
  DBServerEdit, DBNameEdit, DBUsernameEdit, DBPasswordEdit, DBTableEdit, KeyVaultURIEdit: TEdit;

procedure InitializeWizard;
begin
  // Criar página de configuração do banco de dados
  DBConfigPage := CreateInputQueryPage(wpSelectTasks,
    ExpandConstant('{cm:DatabaseConfig}'),
    ExpandConstant('{cm:DatabaseConfigDesc}'),
    '');

  // Adicionar campos para configuração do banco de dados
  DBConfigPage.Add(ExpandConstant('{cm:DBServer}'), False);
  DBConfigPage.Add(ExpandConstant('{cm:DBName}'), False);
  DBConfigPage.Add(ExpandConstant('{cm:DBUsername}'), False);
  DBConfigPage.Add(ExpandConstant('{cm:DBPassword}'), False);
  DBConfigPage.Add(ExpandConstant('{cm:DBTable}'), False);
  DBConfigPage.Add(ExpandConstant('{cm:KeyVaultURI}'), False);

  // Definir valores padrão
  DBConfigPage.Values[4] := 'SeparatorRecords';  // Valor padrão para tabela
  DBConfigPage.Values[5] := 'https://mprkv2024az.vault.azure.net/';  // Valor padrão para Key Vault URI

  // Obter referências para os controles de edição
  DBServerEdit := DBConfigPage.Edits[0];
  DBNameEdit := DBConfigPage.Edits[1];
  DBUsernameEdit := DBConfigPage.Edits[2];
  DBPasswordEdit := DBConfigPage.Edits[3];
  DBTableEdit := DBConfigPage.Edits[4];
  KeyVaultURIEdit := DBConfigPage.Edits[5];

  // Configurar o campo de senha para esconder os caracteres
  DBPasswordEdit.PasswordChar := '*';
end;

[CustomMessages]
english.DatabaseConfig=Database Configuration
portuguese.DatabaseConfig=Configuração do Banco de Dados

english.DatabaseConfigDesc=Configure the database connection parameters
portuguese.DatabaseConfigDesc=Configure os parâmetros de conexão com o banco de dados

english.DBServer=Server:
portuguese.DBServer=Servidor:

english.DBName=Database Name:
portuguese.DBName=Nome do Banco de Dados:

english.DBUsername=Username:
portuguese.DBUsername=Usuário:

english.DBPassword=Password:
portuguese.DBPassword=Senha:

english.DBTable=Table Name:
portuguese.DBTable=Nome da Tabela:

english.KeyVaultURI=Azure Key Vault URI:
portuguese.KeyVaultURI=URI do Azure Key Vault:

[Registry]
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}\Settings"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}\Settings"; ValueType: string; ValueName: "DataPath"; ValueData: "{localappdata}\{#MyAppName}\Data"; Flags: uninsdeletevalue

; Configurações do banco de dados
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "DB_SERVER"; ValueData: "{code:GetDBServer}"; Flags: uninsdeletevalue; Check: not EnvironVarExists('DB_SERVER')
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "DB_NAME"; ValueData: "{code:GetDBName}"; Flags: uninsdeletevalue; Check: not EnvironVarExists('DB_NAME')
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "DB_USERNAME"; ValueData: "{code:GetDBUsername}"; Flags: uninsdeletevalue; Check: not EnvironVarExists('DB_USERNAME')
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "DB_PASSWORD"; ValueData: "{code:GetDBPassword}"; Flags: uninsdeletevalue; Check: not EnvironVarExists('DB_PASSWORD')
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "DB_TABLE"; ValueData: "{code:GetDBTable}"; Flags: uninsdeletevalue; Check: not EnvironVarExists('DB_TABLE')
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "KEY_VAULT_URI"; ValueData: "{code:GetKeyVaultURI}"; Flags: uninsdeletevalue; Check: not EnvironVarExists('KEY_VAULT_URI')
