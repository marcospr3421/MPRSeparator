import logging
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import HttpResponseError



class SecretRetrievalError(Exception):
    pass

def get_secret(secret_name, key_vault_uri):
    """
    Retrieves a secret from Azure Key Vault.

    Args:
        secret_name (str): The name of the secret.
        key_vault_uri (str): The URI of the Azure Key Vault.

    Returns:
        str: The value of the secret.

    """
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
    try:
        secret = secret_client.get_secret(secret_name)
        if secret.value is None:
            raise SecretRetrievalError("Secret value is None")
        return secret.value
    except HttpResponseError as e:
        logging.error(f"Failed to retrieve the secret: {e}")
        raise SecretRetrievalError(f"Failed to retrieve the secret: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise SecretRetrievalError(f"An error occurred: {e}")