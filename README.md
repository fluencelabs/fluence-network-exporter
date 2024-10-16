# fluence-network-exporter

## Configuration

| env variable | description                             | default | required |
| ------------ | --------------------------------------- | ------- | -------- |
| PORT         | exporter listening port                 | 8001    | false    |
| PRIVATE_KEY  | private key to use to send transactions |         | false    |
| CONFIG_FILE  | path to config file                     |         | true     |

```yml
rpc_url: "https://rpc.testnet.fluence.dev"
graph_node_url: 'https://graph-node.stage.fluence.dev/subgraphs/name/fluence-deal-contracts-3d15b6b4'
graph_node_nft_url: 'https://graph-node.stage.fluence.dev/subgraphs/name/fluence-nft-marketplace-dimakortest'

addresses:
  - address: "0x9262768725134b7d52041FAb42287EA2147D0c77"
    name: foobar
    minimum_balance: 100000000

providers:
  - "0x957b816cab1b9e429c3282c8f389f1fd2f8cfe1a"

transaction:
    enabled: true
    interval: "60s"
    private_key_path: "/secrets/private.key" # can be provided in env variable PRIVATE_KEY
```
