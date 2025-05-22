"""Build script for creating the MPR Separator installer"""
import os
import subprocess
import json
import shutil
import argparse
import sys
from pathlib import Path

def get_version():
    """Get the current version from version.json"""
    try:
        with open('version.json', 'r') as f:
            data = json.load(f)
            return data.get('version', '1.0.0')
    except (FileNotFoundError, json.JSONDecodeError):
        return '1.0.0'

def find_main_script():
    """Find the main script file in the project directory"""
    # List of common main file names
    possible_main_files = [
        'app.py', 
        'main.py', 
        'MPRSeparator.py', 
        'run.py',
        'src/main.py',
        'src/app.py'
    ]
    
    # Check for __main__.py in src directory
    src_dir = Path('src')
    if src_dir.exists() and (src_dir / '__main__.py').exists():
        return str(src_dir / '__main__.py')
        
    # Check if any of the possible main files exist
    for main_file in possible_main_files:
        if os.path.exists(main_file):
            return main_file
    
    # List Python files in the root directory
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    if python_files:
        # Ask the user which file is the main file
        print("Could not automatically determine the main script file.")
        print("Available Python files:")
        for i, file in enumerate(python_files, 1):
            print(f"{i}. {file}")
        
        try:
            choice = input("Enter the number of your main script file: ")
            index = int(choice) - 1
            if 0 <= index < len(python_files):
                return python_files[index]
        except (ValueError, IndexError):
            pass
    
    # If no main file is found or selected, raise an error
    raise FileNotFoundError("Could not find the main script file.")

def build_exe():
    """Build the executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Get version for the executable
    version = get_version()
    
    # Clean output directories safely
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
            except PermissionError as e:
                print(f"Aviso: Não foi possível remover o diretório {dir_name}: {str(e)}")
                print("Tentando continuar mesmo assim...")
    
    # Find the main script file
    try:
        main_script = find_main_script()
        print(f"Using main script: {main_script}")
    except FileNotFoundError as e:
        print(str(e))
        print("Please specify the main script file manually.")
        main_script = input("Enter the path to your main script file (e.g., src/main.py): ")
        if not os.path.exists(main_script):
            raise FileNotFoundError(f"The specified file '{main_script}' does not exist.")
    
    # Criar um diretório temporário para o build com permissões adequadas
    import tempfile
    temp_build_dir = tempfile.mkdtemp(prefix='mpr_build_')
    print(f"Usando diretório temporário para build: {temp_build_dir}")
    
    # Run PyInstaller
    pyinstaller_args = [
        'pyinstaller',
        '--name=MPRSeparator',
        '--windowed',
        '--onefile',
        '--clean',
        '--noconfirm',
        f'--workpath={temp_build_dir}',
    ]
    
    # Add icon if it exists
    if os.path.exists('assets/icon.ico'):
        pyinstaller_args.append('--icon=assets/icon.ico')
    else:
        print("Warning: Icon file 'assets/icon.ico' not found. Continuing without icon.")
    
    # Add data files if directories exist
    if os.path.exists('src/translations'):
        pyinstaller_args.append('--add-data=src/translations/;src/translations/')
    
    if os.path.exists('version.json'):
        pyinstaller_args.append('--add-data=version.json;.')
    
    # Add the main script
    pyinstaller_args.append(main_script)
    
    print(f"Running PyInstaller with arguments: {' '.join(pyinstaller_args)}")
    
    try:
        # Execute PyInstaller with lower privileges if possible
        result = subprocess.run(pyinstaller_args, check=False, capture_output=True, text=True)
        
        # Check for errors
        if result.returncode != 0:
            print(f"Erro ao executar PyInstaller (código {result.returncode}):")
            print(result.stderr)
            
            # Tentar identificar problemas comuns
            if "PermissionError" in result.stderr or "Access is denied" in result.stderr:
                print("\nErro de permissão detectado. Sugestões:")
                print("1. Feche todos os programas que possam estar usando arquivos no diretório")
                print("2. Execute este script em um diretório onde você tenha permissões completas")
                print("3. Tente executar o prompt de comando como administrador")
            
            # Limpar diretório temporário
            try:
                shutil.rmtree(temp_build_dir)
            except Exception as cleanup_error:
                print(f"Aviso: Não foi possível limpar o diretório temporário: {str(cleanup_error)}")
            
            return None
        
        # Mostrar saída do PyInstaller para debug
        if result.stdout:
            print("Saída do PyInstaller:\n", result.stdout)
        
        # Copy necessary files to dist directory
        if os.path.exists('version.json'):
            os.makedirs('dist', exist_ok=True)
            shutil.copy('version.json', 'dist/version.json')
        
        # Verificar se o executável foi criado
        exe_path = 'dist/MPRSeparator.exe'
        if os.path.exists(exe_path):
            print(f"Executable built successfully: {exe_path} (v{version})")
        else:
            print(f"Aviso: O executável não foi encontrado em {exe_path}")
            print("Verifique a saída do PyInstaller acima para detalhes.")
    
    except Exception as e:
        print(f"Erro durante o processo de build: {str(e)}")
        return None
    finally:
        # Limpar diretório temporário
        try:
            shutil.rmtree(temp_build_dir)
            print(f"Diretório temporário removido: {temp_build_dir}")
        except Exception as cleanup_error:
            print(f"Aviso: Não foi possível limpar o diretório temporário: {str(cleanup_error)}")
    
    return version

def build_installer(version):
    """Build the installer using Inno Setup"""
    print("Building installer with Inno Setup...")
    
    # Create Inno Setup script
    iss_script = f"""
#define MyAppName "MPR Labs - MPR Separator"
#define MyAppVersion "{version}"
#define MyAppPublisher "MPR Labs"
#define MyAppURL "https://github.com/marcospr3421/MPRSeparator"
#define MyAppExeName "MPRSeparator.exe"

[Setup]
AppId={{{{8A69D345-D564-463C-AFF1-A69D9E530F96}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{localappdata}}\\{{#MyAppName}}
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=MPRSeparator_Setup_v{version}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
CreateAppDir=yes
UninstallDisplayIcon={{app}}\\{{#MyAppExeName}}
SetupLogging=yes
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\\Portuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}";

[Files]
Source: "dist\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "dist\\version.json"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[Dirs]
Name: "{{localappdata}}\\{{#MyAppName}}\\Data"; Permissions: users-full

[Registry]
Root: HKCU; Subkey: "Software\\{{#MyAppPublisher}}\\{{#MyAppName}}"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\\{{#MyAppPublisher}}\\{{#MyAppName}}\\Settings"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\\{{#MyAppPublisher}}\\{{#MyAppName}}\\Settings"; ValueType: string; ValueName: "DataPath"; ValueData: "{{localappdata}}\\{{#MyAppName}}\\Data"; Flags: uninsdeletevalue
"""
    
    # Create installer directory if it doesn't exist
    os.makedirs('installer', exist_ok=True)
    
    # Write Inno Setup script to file
    with open('installer_script.iss', 'w') as f:
        f.write(iss_script)
    
    # Check if Inno Setup is installed
    inno_setup_paths = [
        r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
        r'C:\Program Files\Inno Setup 6\ISCC.exe'
    ]
    
    inno_setup_path = None
    for path in inno_setup_paths:
        if os.path.exists(path):
            inno_setup_path = path
            break
    
    if not inno_setup_path:
        print("Inno Setup not found. Please install it or adjust the path.")
        return False
    
    # Compile installer
    subprocess.run([inno_setup_path, 'installer_script.iss'], check=True)
    
    print(f"Installer built successfully: installer/MPRSeparator_Setup_v{version}.exe")
    return True

def main():
    parser = argparse.ArgumentParser(description='Build MPR Separator executable and installer')
    parser.add_argument('--exe-only', action='store_true', help='Build executable only, no installer')
    parser.add_argument('--main-script', type=str, help='Path to the main script file')
    args = parser.parse_args()
    
    try:
        # Install required packages
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "requests", "packaging"])
        except subprocess.CalledProcessError:
            print("Warning: Could not install required packages. Build process may fail.")
        
        # Build the executable
        version = build_exe()
        
        if not args.exe_only:
            # Build the installer
            build_installer(version)
            
        print("Build process completed successfully!")
            
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Error during build process: {str(e)}")
        return 1
        
    return 0

if __name__ == '__main__':
    exit(main())