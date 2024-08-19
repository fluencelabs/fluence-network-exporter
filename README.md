# gelato-exporter

## Options

| env variable         | description                                          | default | required |
| -------------------- | ---------------------------------------------------- | ------- | -------- |
| RPC_URL              | rpc url                                              |         | true     |
| PORT                 | exporter listening port                              | 8001    | false    |
| PRIVATE_KEY          | private key to use to send transactions              |         | false    |
| TRANSACTION_INTERVAL | how often to perform transactions in seconds         | 60      | false    |
| ADDRESSES_FILE       | yml file with addresses list to gather balances from |         | false    |

If `PRIVATE_KEY` is set exporter will execute transaction to itself once in
`TRANSACTION_INTERVAL` triggering block production.

In order to collect balance of eth addresses specify them in `ADDRESSES_FILE` in
the following format:

```yml
addresses:
  - address: "0x9262768725134b7d52041FAb42287EA2147D0c77"
    name: foobar
```
