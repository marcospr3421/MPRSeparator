"""Script para configurar o ambiente do MPR Separator"""
# Este script configura o ambiente para o MPR Separator, incluindo diretórios de dados
# e variáveis de ambiente para conexão com o banco de dados.
import os
import sys
import winreg
import logging
import subprocess
from pathlib import Path
import ctypes

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_data_directory():
    """Garante que o diretório de dados existe e tem as permissões corretas"""
    try:
        # Obter caminho de dados do registro
        try:
            reg_path = r"Software\MPR Labs\MPR Labs - MPR Separator\Settings"
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
            data_path, _ = winreg.QueryValueEx(registry_key, "DataPath")
            winreg.CloseKey(registry_key)
            logger.info(f"Usando caminho de dados do registro: {data_path}")
        except Exception as reg_error:
            # Definir caminho padrão se a chave do registro não for encontrada
            data_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "MPR Labs - MPR Separator", "Data")
            logger.info(f"Usando caminho de dados padrão: {data_path}")
            
            # Criar a chave do registro se não existir
            try:
                reg_path = r"Software\MPR Labs\MPR Labs - MPR Separator\Settings"
                registry_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                winreg.SetValueEx(registry_key, "DataPath", 0, winreg.REG_SZ, data_path)
                winreg.CloseKey(registry_key)
                logger.info(f"Chave de registro criada para o caminho de dados: {data_path}")
            except Exception as create_reg_error:
                logger.warning(f"Não foi possível criar a chave de registro: {str(create_reg_error)}")
        
        # Garantir que o diretório de dados existe
        os.makedirs(data_path, exist_ok=True)
        logger.info(f"Diretório de dados criado/verificado: {data_path}")
        
        # Verificar se o diretório tem as permissões corretas
        test_file_path = os.path.join(data_path, "test_permissions.txt")
        try:
            with open(test_file_path, 'w') as f:
                f.write("Test file for permissions check")
            os.remove(test_file_path)
            logger.info("Permissões de escrita verificadas com sucesso")
            return True
        except Exception as perm_error:
            logger.error(f"Erro de permissão no diretório de dados: {str(perm_error)}")
            return False
            
    except Exception as e:
        logger.error(f"Erro ao configurar diretório de dados: {str(e)}")
        return False

def check_odbc_driver():
    """Verifica se o driver ODBC 18 para SQL Server está instalado"""
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        target_driver = "ODBC Driver 18 for SQL Server"
        
        if target_driver in drivers:
            logger.info(f"Driver {target_driver} encontrado")
            return True
        else:
            logger.warning(f"Driver {target_driver} não encontrado. Drivers disponíveis: {drivers}")
            
            # Tentar usar um driver alternativo se disponível
            alternative_drivers = [
                "ODBC Driver 17 for SQL Server",
                "SQL Server Native Client 11.0",
                "SQL Server"
            ]
            
            for alt_driver in alternative_drivers:
                if alt_driver in drivers:
                    logger.info(f"Usando driver alternativo: {alt_driver}")
                    
                    # Atualizar o registro para usar o driver alternativo
                    try:
                        reg_path = r"Software\MPR Labs\MPR Labs - MPR Separator\Settings"
                        registry_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                        winreg.SetValueEx(registry_key, "SqlDriver", 0, winreg.REG_SZ, alt_driver)
                        winreg.CloseKey(registry_key)
                        logger.info(f"Registro atualizado para usar o driver: {alt_driver}")
                        return True
                    except Exception as reg_error:
                        logger.warning(f"Não foi possível atualizar o registro: {str(reg_error)}")
            
            logger.error("Nenhum driver SQL Server compatível encontrado")
            return False
            
    except ImportError:
        logger.error("Módulo pyodbc não está instalado")
        return False
    except Exception as e:
        logger.error(f"Erro ao verificar driver ODBC: {str(e)}")
        return False

def set_environment_variables(db_server, db_name, db_username, db_password, db_table, key_vault_uri):
    """Configura as variáveis de ambiente para conexão com o banco de dados"""
    try:
        # Configurar variáveis de ambiente no registro do Windows
        env_vars = {
            "DB_SERVER": db_server,
            "DB_NAME": db_name,
            "DB_USERNAME": db_username,
            "DB_PASSWORD": db_password,
            "DB_TABLE": db_table or "SeparatorRecords",
            "KEY_VAULT_URI": key_vault_uri or "https://mprkv2024az.vault.azure.net/"
        }
        
        # Verificar se há valores vazios e usar valores padrão quando necessário
        if not db_table:
            env_vars["DB_TABLE"] = "SeparatorRecords"
            logger.info("Usando valor padrão para DB_TABLE: SeparatorRecords")
            
        if not key_vault_uri:
            env_vars["KEY_VAULT_URI"] = "https://mprkv2024az.vault.azure.net/"
            logger.info("Usando valor padrão para KEY_VAULT_URI: https://mprkv2024az.vault.azure.net/")
        
        # Definir variáveis de ambiente no registro do Windows
        for var_name, var_value in env_vars.items():
            if var_value:  # Só definir se tiver um valor
                try:
                    # Definir para o processo atual
                    os.environ[var_name] = var_value
                    
                    # Definir no registro para persistir
                    reg_path = r"Environment"
                    registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, 
                                                winreg.KEY_SET_VALUE | winreg.KEY_WRITE)
                    winreg.SetValueEx(registry_key, var_name, 0, winreg.REG_SZ, var_value)
                    winreg.CloseKey(registry_key)
                    logger.info(f"Variável de ambiente {var_name} configurada com sucesso")
                except Exception as e:
                    logger.error(f"Erro ao configurar variável de ambiente {var_name}: {str(e)}")
        
        # Notificar o Windows sobre a mudança nas variáveis de ambiente
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x001A
        SMTO_ABORTIFHUNG = 0x0002
        result = ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0, 
            ctypes.c_wchar_p("Environment"), SMTO_ABORTIFHUNG, 1000, None)
        
        if result == 0:
            logger.warning("Não foi possível notificar o Windows sobre a mudança nas variáveis de ambiente")
        else:
            logger.info("Windows notificado sobre a mudança nas variáveis de ambiente")
            
        return True
    except Exception as e:
        logger.error(f"Erro ao configurar variáveis de ambiente: {str(e)}")
        return False

def main():
    """Função principal para configurar o ambiente"""
    print("Configurando ambiente para MPR Separator...")
    
    # Verificar diretório de dados
    if not ensure_data_directory():
        print("ERRO: Não foi possível configurar o diretório de dados")
        return False
        
    # Verificar driver ODBC
    if not check_odbc_driver():
        print("AVISO: Driver ODBC para SQL Server não encontrado ou não configurado corretamente")
        print("Você pode precisar instalar o Microsoft ODBC Driver para SQL Server")
        print("Visite: https://learn.microsoft.com/pt-br/sql/connect/odbc/download-odbc-driver-for-sql-server")
    
    # Configurar variáveis de ambiente se fornecidas como argumentos
    if len(sys.argv) >= 7:
        db_server = sys.argv[1]
        db_name = sys.argv[2]
        db_username = sys.argv[3]
        db_password = sys.argv[4]
        db_table = sys.argv[5] if len(sys.argv) > 5 else ""
        key_vault_uri = sys.argv[6] if len(sys.argv) > 6 else ""
        
        if set_environment_variables(db_server, db_name, db_username, db_password, db_table, key_vault_uri):
            print("Variáveis de ambiente para conexão com o banco de dados configuradas com sucesso.")
        else:
            print("ERRO: Não foi possível configurar as variáveis de ambiente para conexão com o banco de dados.")
            print("Você pode precisar configurá-las manualmente.")
    else:
        print("AVISO: Parâmetros de conexão com o banco de dados não fornecidos.")
        print("As variáveis de ambiente não foram configuradas.")
    
    print("\nConfiguração de ambiente concluída.")
    print("Agora você deve conseguir executar o aplicativo sem privilégios de administrador.")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Erro não tratado durante a configuração do ambiente: {str(e)}")
        print(f"ERRO: {str(e)}")
        sys.exit(1)
