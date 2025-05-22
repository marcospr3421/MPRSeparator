"""Script para configurar o ambiente do MPR Separator"""
import os
import sys
import winreg
import logging
import subprocess
from pathlib import Path

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
    
    print("\nConfiguração de ambiente concluída.")
    print("Agora você deve conseguir executar o aplicativo sem privilégios de administrador.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
