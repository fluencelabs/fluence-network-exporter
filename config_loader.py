import yaml
from pydantic import BaseModel, ValidationError, constr, conlist, condecimal
from typing import List, Optional
import pathlib
import logging

logger = logging.getLogger(__name__)

# Config schema
class AddressEntry(BaseModel):
    address: constr(min_length=1)
    name: constr(min_length=1)
    minimum_balance: condecimal(ge=0)

class TransactionConfig(BaseModel):
    enabled: bool
    private_key_path: Optional[str] = None
    interval: Optional[str] = "60s"

class ConfigSchema(BaseModel):
    rpc_url: constr(min_length=1)
    graph_node_url: Optional[constr(min_length=1)] = None
    addresses: Optional[conlist(AddressEntry, min_length=1)] = None
    providers: Optional[conlist(constr(min_length=1), min_length=1)] = None
    transaction: Optional[TransactionConfig] = None
    port: Optional[int] = 8001

def load_config(config_file_path: str) -> ConfigSchema:
    """Load and validate the configuration file."""
    try:
        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            config = ConfigSchema(**config_data)
            logger.debug(f"Successfully loaded and validated config from {config_file_path}")
            return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_file_path}. Please provide a valid file path.")
        exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing the YAML file: {config_file_path}. Error: {e}")
        exit(1)
    except ValidationError as e:
        logger.error(f"Configuration validation error: {e.json()}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error while loading config: {e}")
        exit(1)

def load_private_key(private_key_path: Optional[str]) -> Optional[str]:
    """Load a private key from the specified file path."""
    if private_key_path:
        key_path = pathlib.Path(private_key_path)
        if key_path.exists() and key_path.is_file():
            try:
                with open(key_path, 'r') as key_file:
                    private_key = key_file.read().strip()
                    logger.debug(f"Successfully loaded private key from {private_key_path}")
                    return private_key
            except Exception as e:
                logger.error(f"Error reading private key from {private_key_path}: {e}")
                raise
        else:
            logger.error(f"Private key file does not exist or is not a file: {private_key_path}")
            return None
    else:
        return None
