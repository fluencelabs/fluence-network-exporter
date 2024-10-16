import os
import logging
import sys
from prometheus_client import generate_latest
from flask import Flask, Response, cli

import config_loader
import metrics
import network_metrics as nm
import graph_node_metrics as gm
import graph_node_nft_metrics as nftm

# Setup logging
LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Disable Flask's default logging
logging.getLogger("werkzeug").disabled = True
cli.show_server_banner = lambda *x: None

app = Flask(__name__)

registry = metrics.registry


@app.route('/')
def root():
    return "Exporter is running", 200


@app.route('/metrics')
def metrics_endpoint():
    try:
        nm.collect_metrics(rpc, addresses_to_monitor, diamond_address)
        gm.collect_metrics(graph_node, providers_to_monitor)
        nftm.collect_metrics(graph_node_nft)
        return Response(generate_latest(registry), mimetype="text/plain")
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        return Response(
            "Internal Server Error",
            status=500,
            mimetype="text/plain")


if __name__ == '__main__':
    try:
        config_file_path = os.getenv("CONFIG_FILE", "config.yml")
        config = config_loader.load_config(config_file_path)

        rpc_url = config.rpc_url
        graph_node_url = config.graph_node_url
        graph_node_nft_url = config.graph_node_nft_url
        port = int(os.getenv("PORT", str(config.port)))

        addresses_to_monitor = config.addresses
        providers_to_monitor = config.providers
        diamond_address = config.diamond_address

        rpc = nm.connect_rpc(rpc_url)
        graph_node = gm.connect_graph_node(graph_node_url)
        graph_node_nft = nftm.connect_graph_node(graph_node_nft_url)

        if config.transaction and config.transaction.enabled:
            private_key = os.getenv("PRIVATE_KEY") or config_loader.load_private_key(
                config.transaction.private_key_path)
            if private_key:
                transaction_interval = nm.interval_to_seconds(
                    config.transaction.interval)
                nm.start_transaction_task(
                    rpc, private_key, transaction_interval)
            else:
                logger.error(
                    "Transaction is enabled, but the private key could not be loaded. Transactions will not be sent.")

        app.run(host='0.0.0.0', port=port)

    except Exception as e:
        logger.critical(f"Failed to start the application: {e}")
        sys.exit(1)
