import yaml
from pydantic import BaseModel, ValidationError, constr, conlist, condecimal
from typing import List, Optional
import pathlib

import logging
logger = logging.getLogger(__name__)

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
    with open(config_file_path) as file:
        try:
            config_data = yaml.safe_load(file)
            config = ConfigSchema(**config_data)
            return config
        except (ValidationError, yaml.YAMLError) as e:
            logger.error(f"Error loading or validating the config file {config_file_path}: {e}. Exiting.")
            exit(1)

def load_private_key(private_key_path: Optional[str]) -> Optional[str]:
    """Load a private key from the specified file path."""
    if private_key_path and pathlib.Path(private_key_path).exists():
        with open(private_key_path, 'r') as key_file:
            return key_file.read().strip()
    return None
