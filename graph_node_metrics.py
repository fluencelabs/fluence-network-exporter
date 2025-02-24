from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from metrics import *
import based58

import logging
logger = logging.getLogger(__name__)
logging.getLogger("gql").setLevel(logging.WARNING)


def connect_graph_node(graph_node_url):
    """Connect to the Graph Node using the provided URL."""
    try:
        transport = RequestsHTTPTransport(
            url=graph_node_url,
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        logger.info(f"Successfully connected to Graph Node: {graph_node_url}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Graph Node: {e}")
        raise


def get_latest_block(client):
    """Get latest block number"""
    try:
        query = gql('''
        query {
            _meta {
                block {
                    number
                }
            }
        }
        ''')
        response = client.execute(query)
        block = response['_meta']['block']['number']
        FLUENCE_SUBGRAPH_LATEST_BLOCK.set(block)
    except Exception as e:
        logger.error(f"Error fetching latest block number: {e}")
        raise


def get_providers(client):
    """Fetch all providers from the Graph Node."""
    try:
        query = gql('''
        query {
            providers {
                id
                name
            }
        }
        ''')
        response = client.execute(query)
        return response['providers']
    except Exception as e:
        logger.error(f"Error fetching providers: {e}")
        raise


def decode_peer_id(peer_id):
    """Decode the Peer ID to a human-readable format."""
    try:
        fixed_prefix_peer_id = peer_id.replace("0x", "002408011220")
        bytes_peer_id = bytes.fromhex(fixed_prefix_peer_id)
        human_readable_peer_id = based58.b58encode(
            bytes_peer_id).decode('utf-8')
        return human_readable_peer_id
    except Exception as e:
        logger.error(f"Error decoding peer ID: {e}")
        raise


def get_provider_name(client, provider_id):
    """Fetch the provider's name using its ID."""
    try:
        query = gql(f'''
        query {{
            providers(where: {{id: "{provider_id}"}}) {{
                name
            }}
        }}
        ''')
        response = client.execute(query)
        providers = response.get('providers', [])

        if providers:
            return providers[0]['name']
        return None
    except Exception as e:
        logger.error(f"Error fetching provider name for ID {provider_id}: {e}")
        raise


def collect_peer_cc_metrics(client, provider_id, provider_name):
    """Collect Capacity Commitment metrics for peers of a given provider."""
    try:
        query = gql(f'''
        query {{
            peers(where: {{deleted:false,provider_: {{id: "{provider_id}"}}}}) {{
                id
                computeUnitsTotal
                computeUnitsInDeal
                currentCapacityCommitment {{
                    id
                    status
                }}
            }}
        }}
        ''')

        response = client.execute(query)
        peers = response['peers']

        status_mapping = {
            "Inactive": 0,
            "Active": 1,
            "WaitDelegation": 2,
            "WaitStart": 3,
            "Failed": 4,
            "Removed": 5
        }

        for peer in peers:
            peer_id = peer['id']
            peer_id_decoded = decode_peer_id(peer_id)

            if peer['currentCapacityCommitment'] is None:
                FLUENCE_PEER_CC_COUNT.labels(
                    provider_id=provider_id,
                    provider_name=provider_name,
                    peer_id=peer_id_decoded).set(0)
            else:
                FLUENCE_PEER_CC_COUNT.labels(
                    provider_id=provider_id,
                    provider_name=provider_name,
                    peer_id=peer_id_decoded).set(1)
                cc_status = peer['currentCapacityCommitment']['status']
                # Default to 0 if the status is unknown
                status_code = status_mapping.get(cc_status, 0)
                FLUENCE_PEER_CС_STATUS.labels(
                    provider_id=provider_id,
                    provider_name=provider_name,
                    peer_id=peer_id_decoded).set(status_code)

            FLUENCE_PEER_CU_UNIT_TOTAL.labels(
                provider_id=provider_id,
                provider_name=provider_name,
                peer_id=peer_id_decoded).set(
                peer['computeUnitsTotal'])
            FLUENCE_PEER_CU_UNIT_IN_DEAL.labels(
                provider_id=provider_id,
                provider_name=provider_name,
                peer_id=peer_id_decoded).set(
                peer['computeUnitsInDeal'])
    except Exception as e:
        logger.error(
            f"Error collecting peer CC metrics for provider {provider_name} (ID: {provider_id}): {e}")
        raise


def collect_peer_to_deal_metrics(client, provider_id, provider_name):
    """Collect Deal metrics for peers of a given provider."""
    try:
        query = gql(f'''
        query {{
            peers(where: {{provider_: {{id: "{provider_id}"}}}}) {{
                id
                joinedDeals {{
                    id
                }}
            }}
        }}
        ''')

        response = client.execute(query)
        peers = response['peers']

        for peer in peers:
            peer_id = peer['id']
            peer_id_decoded = decode_peer_id(peer_id)
            joined_deals_count = len(peer['joinedDeals'])

            FLUENCE_PEER_JOINED_DEALS.labels(
                provider_id=provider_id,
                provider_name=provider_name,
                peer_id=peer_id_decoded).set(joined_deals_count)
    except Exception as e:
        logger.error(
            f"Error collecting peer to deal metrics for provider {provider_name} (ID: {provider_id}): {e}")
        raise


def collect_deal_metrics(client, provider_id, provider_name):
    """Collect general Deal metrics for a given provider."""
    try:
        query = gql(f'''
        query {{
            dealToPeers(where: {{peer_: {{provider: "{provider_id}"}}}}) {{
                deal {{
                    id
                    createdAt
                }}
            }}
        }}
        ''')

        response = client.execute(query)
        deals = response['dealToPeers']

        unique_deal_ids = set(deal['deal']['id'] for deal in deals)
        active_deals_count = len(unique_deal_ids)
        FLUENCE_DEAL_ACTIVE.labels(
            provider_id=provider_id,
            provider_name=provider_name).set(active_deals_count)

        for deal in deals:
            deal_id = deal['deal']['id']
            deal_created_at = deal['deal']['createdAt']
            FLUENCE_DEAL_ACTIVE_START_DATE.labels(
                provider_id=provider_id,
                provider_name=provider_name,
                deal_id=deal_id).set(deal_created_at)
    except Exception as e:
        logger.error(
            f"Error collecting deal metrics for provider {provider_name} (ID: {provider_id}): {e}")
        raise

def collect_active_capacity_commitments_stats(client, provider_id, provider_name):
    try:
        query = gql(f'''
        query {{
            capacityCommitments(where:{{ and: [{{status: Active}}, {{provider_: {{id: "{provider_id}"}}}}]}}) {{
                id
                status
                totalFailCount
                submittedProofsCount
            }}
        }}
        ''')
        response = client.execute(query)
        capacity_commitments = response['capacityCommitments']

        for cc in capacity_commitments:
            cc_id = cc['id']
            totalFailCount = cc['totalFailCount']
            submittedProofsCount = cc['submittedProofsCount']

            COMMITMENT_TOTAL_FAILED_PROOFS.labels(
                cc_id=cc_id,
                provider_id=provider_id,
                provider_name=provider_name).set(totalFailCount)
            COMMITMENT_SUBMITTED_PROOFS.labels(
                cc_id=cc_id,
                provider_id=provider_id,
                provider_name=provider_name).set(submittedProofsCount)
    except Exception as e:
        logger.error(f"Error collecting active capacity commitments: {e}")
        raise

def collect_graph_networks_metrics(client):
    try:
        query = gql('''
        query {
            graphNetworks {
                fltPrice
                slashingRate
                coreEpochDuration
                capacityMaxFailedRatio
                usdTargetRevenuePerEpoch
                minRequiredProofsPerEpoch
                dealsTotal
                proofsTotal
                offersTotal
                providersRegisteredTotal
                approvedProviders
                effectorsTotal
                capacityCommitmentsTotal
                usdCollateralPerUnit
                minRewardPerEpoch
                maxRewardPerEpoch
                vestingPeriodDuration
                vestingPeriodCount
                maxProofsPerEpoch
                withdrawEpochsAfterFailed
                difficulty
            }
        }
        ''')

        response = client.execute(query)

        graphNetwork = response['graphNetworks'][0]

        fltPrice = graphNetwork['fltPrice']
        slashingRate = graphNetwork['slashingRate']
        coreEpochDuration = graphNetwork['coreEpochDuration']
        capacityMaxFailedRatio = graphNetwork['capacityMaxFailedRatio']
        usdTargetRevenuePerEpoch = graphNetwork['usdTargetRevenuePerEpoch']
        minRequiredProofsPerEpoch = graphNetwork['minRequiredProofsPerEpoch']
        dealsTotal = graphNetwork['dealsTotal']
        proofsTotal = graphNetwork['proofsTotal']
        offersTotal = graphNetwork['offersTotal']
        providersRegisteredTotal = graphNetwork['providersRegisteredTotal']
        approvedProviders = graphNetwork['approvedProviders']
        effectorsTotal = graphNetwork['effectorsTotal']
        commitmentCreatedCount = graphNetwork['capacityCommitmentsTotal']
        usdCollateralPerUnit = graphNetwork['usdCollateralPerUnit']
        minRewardPerEpoch = graphNetwork['minRewardPerEpoch']
        maxRewardPerEpoch = graphNetwork['maxRewardPerEpoch']
        vestingPeriodDuration = graphNetwork['vestingPeriodDuration']
        vestingPeriodCount = graphNetwork['vestingPeriodCount']
        maxProofsPerEpoch = graphNetwork['maxProofsPerEpoch']
        withdrawEpochsAfterFailed = graphNetwork['withdrawEpochsAfterFailed']
        difficulty = graphNetwork['difficulty']

        FLT_PRICE.set(fltPrice)
        SLASHING_RATE.set(slashingRate)
        CORE_EPOCH_DURATION.set(coreEpochDuration)
        CAPACITY_MAX_FAILED_RATIO.set(capacityMaxFailedRatio)
        USD_TARGET_REVENUE_PER_EPOCH.set(usdTargetRevenuePerEpoch)
        MIN_REQUIRED_PROOFS_PER_EPOCH.set(minRequiredProofsPerEpoch)
        DEALS_TOTAL.set(dealsTotal)
        PROOFS_TOTAL.set(proofsTotal)
        OFFERS_TOTAL.set(offersTotal)
        PROVIDERS_TOTAL.set(providersRegisteredTotal)
        APPROVED_PROVIDERS.set(approvedProviders)
        EFFECTORS_TOTAL.set(effectorsTotal)
        COMMITMENT_CREATED_COUNT.set(commitmentCreatedCount)
        USD_COLLATERAL_PER_UNIT.set(usdCollateralPerUnit)
        MIN_REWARD_PER_EPOCH.set(minRewardPerEpoch)
        MAX_REWARD_PER_EPOCH.set(maxRewardPerEpoch)
        VESTING_PERIOD_DURATION.set(vestingPeriodDuration)
        VESTING_PERIOD_COUNT.set(vestingPeriodCount)
        MAX_PROOFS_PER_EPOCH.set(maxProofsPerEpoch)
        WITHDRAW_EPOCHS_AFTER_FAILED.set(withdrawEpochsAfterFailed)
        INFO.info({'name': 'difficulty', 'difficulty': difficulty})

    except Exception as e:
        logger.error(f"Error collecting graph networks: {e}")
        raise

def collect_metrics(graph_node, providers_to_monitor):
    try:
        get_latest_block(graph_node)
        collect_graph_networks_metrics(graph_node)
        if providers_to_monitor:
            for provider_id in providers_to_monitor:
                provider_name = get_provider_name(graph_node, provider_id)

                if provider_name:
                    collect_peer_cc_metrics(
                        graph_node, provider_id, provider_name)
                    collect_peer_to_deal_metrics(
                        graph_node, provider_id, provider_name)
                    collect_deal_metrics(
                        graph_node, provider_id, provider_name)
                    collect_active_capacity_commitments_stats(
                        graph_node, provider_id, provider_name)
                else:
                    logger.error(
                        f"Could not find provider with ID: {provider_id}")
    except Exception as e:
        logger.error(f"Error in collecting metrics from graph-node: {e}")
        raise ()
