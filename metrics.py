from prometheus_client import Gauge, CollectorRegistry, Info
import config_loader
import os

registry = CollectorRegistry()

FLUENCE_BLOCK_HEIGHT = Gauge('fluence_network_block_height', 'The latest block height', registry=registry)
FLUENCE_BALANCE = Gauge('fluence_network_balance', 'Balance of addresses', ['address', 'name'], registry=registry)
FLUENCE_BALANCE_MINIMUM = Gauge('fluence_network_balance_minimum', 'Minimum balance threshold for addresses', ['address', 'name'], registry=registry)

config_file_path = os.getenv("CONFIG_FILE", "config.yml")
config = config_loader.load_config(config_file_path)
if config.transaction and config.transaction.enabled:
    FLUENCE_TRANSACTION_STATUS = Gauge('fluence_network_transaction_status', 'Indicates status of the last transaction (0=Success, 1=Failure)', registry=registry)

FLUENCE_PEER_CU_UNIT_TOTAL = Gauge('fluence_network_peer_cu_unit_total', 'Total Compute Units on Peer', ['provider_id','provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_CU_UNIT_IN_DEAL = Gauge('fluence_network_peer_cu_unit_in_deal', 'Compute Units occupied by deal on Peer', ['provider_id','provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_CС_STATUS=Gauge('fluence_network_peer_cc_status', "Status of Capacity Commitment of Peer", ['provider_id', 'provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_CC_COUNT=Gauge('fluence_network_peer_cc_count',"Count of Capacity Commitments", ['provider_id','provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_JOINED_DEALS=Gauge('fluence_network_peer_joined_deals_count','Count of Deals on Peer', ['provider_id', 'provider_name', 'peer_id'], registry=registry)

FLUENCE_DEAL_ACTIVE = Gauge('fluence_network_deal_active_total','Total deals active',['provider_id','provider_name'], registry=registry)
FLUENCE_DEAL_ACTIVE_START_DATE=Gauge('fluence_network_deal_active_start_date', 'Duration of a deal', ['provider_id', 'provider_name', 'deal_id'], registry=registry)

FLUENCE_SUBGRAPH_LATEST_BLOCK = Gauge('fluence_network_subgraph_latest_block','The latest block number seen by subgraph', registry=registry)

REWARD_BALANCE_FLT = Gauge('fluence_network_reward_balance', 'Amount of FLT designated to Capacity Rewards on Diamond (scaled to ether)', registry=registry)
POOL_BALANCE_USDC = Gauge('fluence_network_pool_balance', 'Amount of USDC designated to Gateway Pool on Balance Keeper', registry=registry)

TOTAL_CAPACITY_REWARD_FLT = Gauge('fluence_network_total_capacity_rewards', 'Total Amount of FLT designated to Capacity Rewards on Diamond (scaled to ether)', registry=registry)
UNLOCKED_CAPACITY_REWARD_FLT = Gauge('fluence_network_unlocked_rewards', 'Amount of unlocked rewards in FLT (scaled to ether)', registry=registry)
WITHDRAWN_CAPACITY_REWARD_FLT = Gauge('fluence_network_withdrawn_rewards', 'Amount of withdrawn rewards in FLT (scaled to ether)', registry=registry)
TOTAL_DEAL_STAKER_REWARD_FLT = Gauge('fluence_network_deal_staker_rewards', 'Amount of deal staker rewards in FLT (scaled to ether)', registry=registry)

FLT_PRICE = Gauge("fluence_network_flt_price", "Price of FLT in USD", registry=registry)
USD_COLLATERAL_PER_UNIT = Gauge("fluence_network_usd_collateral_per_unit", "USD collateral per compute unit", registry=registry)
MIN_REWARD_PER_EPOCH = Gauge("fluence_network_min_reward_per_epoch", "Min reward per epoch", registry=registry)
MAX_REWARD_PER_EPOCH = Gauge("fluence_network_max_reward_per_epoch", "Max reward per epoch", registry=registry)
VESTING_PERIOD_DURATION = Gauge("fluence_network_vesting_period_duration", "Vesting period duration", registry=registry)
VESTING_PERIOD_COUNT = Gauge("fluence_network_vesting_period_count", "Vesting period count", registry=registry)
MAX_PROOFS_PER_EPOCH = Gauge("fluence_network_max_proofs_per_epoch", "Maximum proofs per epoch", registry=registry)
WITHDRAW_EPOCHS_AFTER_FAILED = Gauge("fluence_network_withdraw_epochs_after_failed", "Withdraw epochs after failed", registry=registry)
SLASHING_RATE = Gauge("fluence_network_slashing_rate", "Slashing rate in percents", registry=registry)

CORE_EPOCH_DURATION = Gauge("fluence_network_core_epoch_duration", "Epoch Duration in seconds", registry=registry)
CORE_CURRENT_EPOCH_START = Gauge("fluence_network_core_current_epoch_start", "Current epoch start", registry=registry)

CAPACITY_MAX_FAILED_RATIO = Gauge("fluence_network_capacity_max_failed_ratio", "CC maximum failed epochs", registry=registry)
USD_TARGET_REVENUE_PER_EPOCH = Gauge("fluence_network_usd_target_revenue_per_epoch", "Target revenue per CC per epoch in non-scaled USD", registry=registry)
MIN_REQUIRED_PROOFS_PER_EPOCH = Gauge("fluence_network_min_required_proofs_per_epoch", "Minimum proofs per CU per epoch", registry=registry)
DEALS_TOTAL = Gauge("fluence_network_deals_total", "Total count of created deals", registry=registry)
PROOFS_TOTAL = Gauge("fluence_network_proofs_total", "Total count of submitted proofs", registry=registry)
OFFERS_TOTAL = Gauge("fluence_network_offers_total", "Total count of created offers", registry=registry)
PROVIDERS_TOTAL = Gauge("fluence_network_providers_total", "Total count of providers", registry=registry)
APPROVED_PROVIDERS = Gauge("fluence_network_approved_providers_total", "Total count of approved providers", registry=registry)
EFFECTORS_TOTAL = Gauge("fluence_network_effectors_total", "Total count of effectors", registry=registry)
COMMITMENT_CREATED_COUNT = Gauge("fluence_network_commitment_created_count", "Total count of CommitmentCreated events", registry=registry)
COMMITMENT_TOTAL_FAILED_CUS = Gauge("fluence_network_cc_total_failed_cus", "Total count of failed CU",['cc_id','provider_id','provider_name'], registry=registry)
COMMITMENT_SUBMITTED_PROOFS = Gauge("fluence_network_cc_submitted_proofs", "Total count of submitted proofs", ['cc_id','provider_id','provider_name'], registry=registry)
COMMITMENT_CURRENT_EPOCH_SUBMITTED_PROOFS = Gauge("fluence_network_cc_current_epoch_submitted_proofs", "Current epoch submitted proofs", ['cc_id','provider_id','provider_name'], registry=registry)
COMMITMENT_CURRENT_EPOCH_MIN_PROJECTED_PROOFS = Gauge("fluence_network_cc_current_epoch_min_projected_proofs", "Current epoch projected proofs (min)", ['cc_id','provider_id','provider_name'], registry=registry)
COMMITMENT_CURRENT_EPOCH_MAX_PROJECTED_PROOFS = Gauge("fluence_network_cc_current_epoch_max_projected_proofs", "Current epoch projected proofs (max)", ['cc_id','provider_id','provider_name'], registry=registry)
COMMITMENT_CURRENT_UNITS = Gauge("fluence_network_cc_current_epoch_cus", "Current epoch CUs stat", ['cc_id','provider_id','provider_name','status'], registry=registry)

INFO = Info("fluence_network_info", "Info about network", registry=registry)
