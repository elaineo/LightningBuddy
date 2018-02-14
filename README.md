# LightningBuddy

Twitter relay for Lightning JSON-RPC interface.

LightningBuddy is a library that can be used to talk to a lightning node from a Twitter account. See the [LightningBuddy API](https://github.com/elaineo/LightningBuddy/wiki/LightningBuddy-Commands) in the wiki.

## Getting started
Install `bitcoind` and `lnd`: https://github.com/lightningnetwork/lnd

**Or**, Install bitcoind and c-Lightning: https://github.com/ElementsProject/lightning

### Install LightningBuddy:
```
git clone https://github.com/elaineo/LightningBuddy
cd LightningBuddy
```
### Install Dependencies

If using c-Lightning, install `pylightning` and skip to **Config.py**.

```
pip install pylightning
```

If using LND, set up a Python gRPC client for the Lightning Network Daemon. ([Instructions here](http://dev.lightning.community/guides/python-grpc/), or just copy the stuff below)

```
pip install grpcio grpcio-tools googleapis-common-protos TwitterAPI
git clone https://github.com/googleapis/googleapis.git
curl -o rpc.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto
```
Compile the proto file:
```
python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto
```

### Config.py

Fill in `config.py`:
```
#!/usr/bin/env python

# Twitter API keys
twitter = { 'consumer_key': '',
            'consumer_secret': '',
            'access_token': '',
            'access_token_secret': '' }
            
# Replace with your own name
twitter_owner = 'Elaine0u' 

## Default Channel creation parameters
CHANNEL_AMOUNT = 100000  # in satoshis

DB_PATH = 'sqlite.db'

"""
Required for c-Lightning
"""
LN_PATH = '/root/.lightning'

"""
Required for LND
"""
# Lnd cert is at ~/.lnd/tls.cert on Linux and
# ~/Library/Application Support/Lnd/tls.cert on Mac
LND_CERT_PATH = '~/.lnd/tls.cert'
LND_HOST = 'localhost:1000X'
NODE_ADDRESS = '<external_ip_addr>'
NODE_PORT = 9735
```
