# LightningBuddy

Twitter relay for Lightning JSON-RPC interface.

LightningBuddy is a library that can be used to talk to a lightning node from a Twitter account. See the [LightningBuddy API](https://github.com/elaineo/LightningBuddy/wiki) in the wiki.

### Getting started
Install `bitcoind` and `lnd`: https://github.com/lightningnetwork/lnd


Install LightningBuddy:
```
git clone https://github.com/elaineo/LightningBuddy
cd LightningBuddy
```
Setup a Python gRPC client for the Lightning Network Daemon. ([Instructions here](http://dev.lightning.community/guides/python-grpc/), or just copy the stuff below)

Install dependencies:
```
pip install grpcio grpcio-tools googleapis-common-protos TwitterAPI
git clone https://github.com/googleapis/googleapis.git
curl -o rpc.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/rpc.proto
```
Compile the proto file:
```
python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. rpc.proto
```
