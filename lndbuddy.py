from tweet import TweetClient
import config as cfg

from db import LightningDB
import os
import json
import random
import logging

import sys
sys.path.insert(0, 'googleapis')

import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import grpc

class LightningWrapper:
    """API for Lightning gRPC client
    """
    def __init__(self, host, creds):
        channel = grpc.secure_channel(host, creds)
        self.stub = lnrpc.LightningStub(channel)

    def get_uri(self):
        try:
            request = ln.GetInfoRequest()
            response = self.stub.GetInfo(request)
            logging.info(response)
            node_id = response.identity_pubkey
            return "%s" % node_id
        except grpc.RpcError as e:
           logging.error(e)

    def get_invoice(self, amount, label, description=None):
        try:
            request = ln.Invoice(
                memo="%s: %s" % (label, description),
                value=amount
            )
            response = self.stub.AddInvoice(request)
            logging.info(response)
            return response.payment_request
        except grpc.RpcError as e:
           logging.error(e)

    def _pay(self, bolt11):
        try:
            request = ln.SendRequest(
                payment_request=bolt11
            )
            response = self.stub.SendPaymentSync(request)
            logging.info(response)
            return response.payment_preimage.decode("utf-8") 
        except grpc.RpcError as e:
           logging.error(e)

    def _connect(self, node_id, host=None, port=9735):
        addr = ln.LightningAddress( 
            pubkey=node_id, 
            host="%s:%s" % (host, port)
            )
        try:
            request = ln.ConnectPeerRequest(
                addr=addr
            )
            response = self.stub.ConnectPeer(request)
            logging.info(response)
            return "Connected %s" % node_id
        except grpc.RpcError as e:
           logging.error(e)

    def _fundchannel(self, node_id, satoshis=cfg.CHANNEL_AMOUNT):
        try:
            request = ln.OpenChannelRequest(
                node_pubkey_string=node_id,
                local_funding_amount=satoshis
            )
            response = self.stub.OpenChannelSync(request)
            logging.info(response)
            return response.funding_txid_str
        except grpc.RpcError as e:
           logging.error(e)
        


def main():
    logging.basicConfig(level=logging.INFO)

    cert = open(os.path.expanduser(cfg.LND_CERT_PATH)).read()
    creds = grpc.ssl_channel_credentials(cert)
    
    lnclient = LightningWrapper(cfg.LND_HOST, creds)

    db = LightningDB(cfg.DB_PATH)

    tweet = TweetClient(cfg.twitter, db, cfg.twitter_owner, lnclient)
    tweet.watch()

if __name__ == "__main__":
    main()