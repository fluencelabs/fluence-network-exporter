from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from metrics import *

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

def collect_metrics(graph_node):
    try:
        query = gql(f'''
        query {{
            marketplace(id:"Marketplace") {{
                tokensTotal
                tokensOnSale
                totalSold
                totalVolume
            }}
        }}
        ''')

        response = graph_node.execute(query)
        nfts = response['marketplace']
        NFTS_TOKENS_TOTAL.set(nfts['tokensTotal'])
        NFTS_TOKENS_ON_SALE.set(nfts['tokensOnSale'])
        NFTS_TOTAL_SOLD.set(nfts['totalSold'])
        NFTS_TOTAL_VOLUME.set(nfts['totalVolume'])
    except Exception as e:
        logger.error(f"Error in collecting NFT metrics from graph-node: {e}")
        raise ()
