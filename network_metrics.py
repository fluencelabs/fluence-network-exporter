from metrics import *
from web3 import Web3
import time
import threading
from config_loader import AddressEntry
import logging

# Set up logging
logger = logging.getLogger(__name__)


def connect_rpc(url: str) -> Web3:
    """Connect to RPC."""
    try:
        web3 = Web3(Web3.HTTPProvider(url))
        if web3.is_connected():
            logger.info(f"Successfully connected to the RPC endpoint: {url}")
            return web3
        else:
            raise ConnectionError(
                f"Failed to connect to the RPC endpoint: {url}")
    except Exception as e:
        logger.error(f"Error connecting to RPC endpoint {url}: {e}")
        raise


def send_transaction(web3: Web3, private_key: str) -> bool:
    """Function to send transaction."""
    try:
        account = web3.eth.account.from_key(private_key)
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
        try:
            gas = web3.eth.estimate_gas(transaction)
            transaction['gas'] = gas
        except Exception as e:
            logger.error(f"Failed to estimate gas for transaction: {str(e)}")
            return False

        transaction['gasPrice'] = web3.eth.gas_price

        signed_txn = web3.eth.account.sign_transaction(
            transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            logger.debug(
                f"Transaction successful: {tx_hash.hex()} with estimated gas: {gas}")
            return True
        else:
            logger.error(f"Transaction {tx_hash.hex()} failed: {transaction}")
            return False
    except Exception as e:
        logger.error(f"Transaction error: {str(e)}")
        return False


def interval_to_seconds(interval: str) -> int:
    """Convert interval to seconds."""
    try:
        time_multiplier = {'s': 1, 'm': 60, 'h': 3600}
        unit = interval[-1]
        if unit not in time_multiplier:
            raise ValueError(
                f"Invalid time unit in interval: {interval}. Valid units are s, m and h")
        return int(interval[:-1]) * time_multiplier[unit]
    except ValueError as e:
        logger.error(f"Interval conversion error: {e}")
        raise


def start_transaction_task(web3: Web3, private_key: str, interval: int):
    """Start a background task to periodically send transaction to RPC."""
    def task():
        while True:
            success = send_transaction(web3, private_key)
            FLUENCE_TRANSACTION_STATUS.set(0 if success else 1)
            time.sleep(interval)

    try:
        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()
        logger.info(
            f"Transaction task started with interval {interval} seconds")
    except Exception as e:
        logger.error(f"Failed to start transaction task: {e}")
        raise


def collect_balances(rpc: Web3, addresses_to_monitor: list[AddressEntry]):
    for entry in addresses_to_monitor:
        address = entry.address
        name = entry.name
        minimum_balance = entry.minimum_balance

        balance_wei = rpc.eth.get_balance(address)
        balance_eth = rpc.from_wei(balance_wei, 'ether')

        FLUENCE_BALANCE.labels(
            address=address, name=name).set(balance_eth)
        logger.debug(f"Address {address} ({name}) balance is: {
                     balance_eth} FLT")
        FLUENCE_BALANCE_MINIMUM.labels(
            address=address, name=name).set(minimum_balance)

        if balance_eth < minimum_balance:
            logger.warning(
                f"Address {address} ({name}) has a balance below the minimum threshold: {balance_eth} < {minimum_balance}")
        else:
            logger.debug(
                f"Address {address} ({name}) has sufficient balance: {balance_eth} FLT")


def collect_reward_balance(rpc: Web3, diamond_address: str):
    abi = '[{"type":"function","name":"getRewardBalance","inputs":[],"outputs":[{"name":"","type":"uint256","internalType":"uint256"}],"stateMutability":"view"}]'
    diamond = rpc.eth.contract(address=diamond_address, abi=abi)
    reward_balance = diamond.functions.getRewardBalance().call()
    reward_balance_eth = rpc.from_wei(reward_balance, 'ether')
    REWARD_BALANCE_FLT.set(reward_balance_eth)
    logger.debug(f"Diamond {diamond_address} reward balance is {
                 reward_balance_eth} FLT")


def collect_metrics(
    rpc: Web3,
    addresses_to_monitor: list[AddressEntry],
    diamond_address: str
):
    """Collect block height and address balances"""
    try:
        latest_block_height = rpc.eth.block_number
        FLUENCE_BLOCK_HEIGHT.set(latest_block_height)
        logger.debug(f"Collected block height: {latest_block_height}")
        if addresses_to_monitor:
            collect_balances(rpc, addresses_to_monitor)
        if diamond_address:
            collect_reward_balance(rpc, diamond_address)

    except Exception as e:
        logger.error(f"Error collecting network metrics: {e}")
        raise
