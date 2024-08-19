# gelato-exporter

## Options

| env variable          | description                                          | default | required |
| --------------------- | ---------------------------------------------------- | ------- | -------- |
| RPC_URL               | rpc url                                              |         | true     |
| PORT                  | exporter listening port                              | 8001    | false    |
| PRIVATE_KEY           | private key to use to send transactions              |         | false    |
| TRANSACTIONS_INTERVAL | how often to perform transactions in seconds         | 60      | false    |
| ADDRESSES_FILE        | yml file with addresses list to gather balances from |         | false    |

Addresses file has the following format:

```yml
addresses:
  - address: "0x9262768725134b7d52041FAb42287EA2147D0c77"
    name: foobar
```
