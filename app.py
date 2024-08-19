import os
import yaml
import logging
import sys
from web3 import Web3
from prometheus_client import Gauge, generate_latest, CollectorRegistry
from flask import Flask, Response
from tenacity import retry, wait_exponential, stop_after_attempt, before_sleep_log
from pydantic import BaseModel, ValidationError, constr, conlist
from typing import List, Optional
import time
import threading

# Setup logging
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)
# Disable flask logging
logging.getLogger("werkzeug").disabled = True
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# Initialize prometheus registry
registry = CollectorRegistry()

# Define schema for a file with addresses to scrape balance of
class AddressEntry(BaseModel):
    address: constr(min_length=1)
    name: constr(min_length=1)

class ConfigSchema(BaseModel):
    addresses: Optional[conlist(AddressEntry, min_length=1)]

def initialize():
    rpc_url = os.getenv("RPC_URL")
    addresses_file = os.getenv("ADDRESSES_FILE")
    private_key = os.getenv("PRIVATE_KEY")
    transaction_interval = int(os.getenv("TRANSACTION_INTERVAL", 60))
    port = int(os.getenv("PORT", 8001))

    if not rpc_url:
        logger.error("RPC_URL is required to connect to the blockchain. Exiting.")
        exit(1)

    addresses_to_monitor = []

    if addresses_file:
        if os.path.exists(addresses_file):
            logger.info(f"Addresses file found: {addresses_file}")
            with open(addresses_file, 'r') as file:
                try:
                    config_data = yaml.safe_load(file)
                    config = ConfigSchema(**config_data)
                    addresses_to_monitor = config.addresses or []
                except (ValidationError, yaml.YAMLError) as e:
                    logger.error(f"Error loading or validating the addresses file {addresses_file}: {e}. Exiting.")
                    exit(1)
        else:
            logger.error(f"Addresses file '{addresses_file}' does not exist. Exiting.")
            exit(1)
    else:
        logger.info("No addresses file provided. No balances will be monitored.")

    return rpc_url, addresses_to_monitor, private_key, transaction_interval, port

# Retry configuration for connecting to the RPC endpoint
@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before_sleep=before_sleep_log(logger, logging.INFO)
)
def connect_rpc(url):
    web3 = Web3(Web3.HTTPProvider(url))
    if web3.is_connected():
        logger.info(f"Successfully connected to the RPC endpoint: {url}")
        return web3
    else:
        raise ConnectionError(f"Failed to connect to the RPC endpoint: {url}")

def send_transaction(web3, private_key):
    account = web3.eth.account.from_key(private_key)
    try:
        chain_id = web3.eth.chain_id
        nonce = web3.eth.get_transaction_count(account.address)

        transaction = {
            'from': account.address,
            'to': account.address,  # Sending to self
            'value': web3.to_wei(0.01, 'ether'),
            'nonce': nonce,
            'chainId': chain_id
        }

        # Estimate gas cost
        gas = web3.eth.estimate_gas(transaction)
        transaction['gas'] = gas
        transaction['gasPrice'] = web3.eth.gas_price

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            logger.info(f"Transaction successful: {tx_hash.hex()} with estimated gas: {gas}")
            return True
        else:
            logger.error(f"Transaction failed: {tx_hash.hex()}")
            return False
    except Exception as e:
        logger.error(f"Transaction error: {str(e)}")
        return False

# Background task to periodically send transactions
def start_transaction_task(web3, private_key, interval):
    def task():
        while True:
            success = send_transaction(web3, private_key)
            transaction_success_metric.set(1 if success else 0)
            time.sleep(interval)

    if private_key:
        thread = threading.Thread(target=task)
        thread.daemon = True
        transaction_success_metric = Gauge('gelato_transaction_success', 'Indicates if the last transaction was successful', registry=registry)
        thread.start()
    else:
        logger.info("No PRIVATE_KEY provided. Transactions will not be sent.")

rpc_url, addresses_to_monitor, private_key, transaction_interval, port = initialize()
web3 = connect_rpc(rpc_url)

app = Flask(__name__)

# Initialize Prometheus metrics
block_height_metric = Gauge('gelato_block_height', 'The latest block height', registry=registry)

def collect_metrics():
    latest_block_height = web3.eth.block_number
    block_height_metric.set(latest_block_height)

    if addresses_to_monitor:
        balance_metrics = Gauge('gelato_balance', 'Balance of Ethereum addresses', ['address', 'name'], registry=registry)
        for entry in addresses_to_monitor:
            address = entry.address
            name = entry.name
            balance_wei = web3.eth.get_balance(address)
            balance_eth = web3.from_wei(balance_wei, 'ether')
            balance_metrics.labels(address=address, name=name).set(balance_eth)

@app.route('/')
def root():
    return "Exporter is running", 200

@app.route('/metrics')
def metrics():
    collect_metrics()
    return Response(generate_latest(registry), mimetype='text/plain')

if __name__ == '__main__':
    start_transaction_task(web3, private_key, transaction_interval)
    app.run(host='0.0.0.0', port=port)
