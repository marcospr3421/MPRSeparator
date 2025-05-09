from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import logging

class AzureKeyVaultClient:
    def __init__(self, vault_url="https://mprkv2024az.vault.azure.net/"):
        """Initialize Azure Key Vault client with the specified vault URL"""
        self.vault_url = vault_url
        try:
            self.credential = DefaultAzureCredential()
            self.client = SecretClient(vault_url=self.vault_url, credential=self.credential)
        except Exception as e:
            logging.error(f"Failed to initialize Azure Key Vault client: {str(e)}")
            raise

    def get_secret(self, secret_name):
        """Retrieve a secret from Azure Key Vault by name"""
        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logging.error(f"Failed to retrieve secret '{secret_name}': {str(e)}")
            raise

def get_sql_connection_string():
    """Get SQL connection string from Azure Key Vault"""
    try:
        vault_client = AzureKeyVaultClient()
        # Get full connection string from Key Vault
        conn_string = vault_client.get_secret("SqlConnString")
        return conn_string
    except Exception as e:
        logging.error(f"Error getting SQL connection string: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    try:
        conn_string = get_sql_connection_string()
        print(f"Successfully retrieved connection string")
        # Don't print the actual connection string in production code
    except Exception as e:
        print(f"Error: {str(e)}")