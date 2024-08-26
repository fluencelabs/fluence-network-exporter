from prometheus_client import Gauge, CollectorRegistry

registry = CollectorRegistry()

FLUENCE_BLOCK_HEIGHT = Gauge('fluence_network_block_height', 'The latest block height', registry=registry)
FLUENCE_BALANCE = Gauge('fluence_network_balance', 'Balance of addresses', ['address', 'name'], registry=registry)
FLUENCE_BALANCE_MINIMUM = Gauge('fluence_network_balance_minimum', 'Minimum balance threshold for addresses', ['address', 'name'], registry=registry)
FLUENCE_TRANSACTION_STATUS = Gauge('fluence_network_transaction_status', 'Indicates status of the last transaction (0=Success, 1=Failure)', registry=registry)

FLUENCE_PEER_CU_UNIT_TOTAL = Gauge('fluence_network_peer_cu_unit_total', 'Total Compute Units on Peer', ['provider_id','provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_CU_UNIT_IN_DEAL = Gauge('fluence_network_peer_cu_unit_in_deal', 'Compute Units occupied by deal on Peer', ['provider_id','provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_CС_STATUS=Gauge('fluence_network_peer_cc_status', "Status of Capacity Commitment of Peer", ['provider_id', 'provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_CC_COUNT=Gauge('fluence_network_peer_cc_count',"Count of Capacity Commitments", ['provider_id','provider_name', 'peer_id'], registry=registry)
FLUENCE_PEER_JOINED_DEALS=Gauge('fluence_network_peer_joined_deals_count','Count of Deals on Peer', ['provider_id', 'provider_name', 'peer_id'], registry=registry)

FLUENCE_DEAL_ACTIVE = Gauge('fluence_network_deal_active_total','Total deals active',['provider_id','provider_name'], registry=registry)
FLUENCE_DEAL_ACTIVE_START_DATE=Gauge('fluence_network_deal_active_start_date', 'Duration of deel', ['provider_id', 'provider_name', 'deal_id'], registry=registry)