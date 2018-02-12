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


def main():
    logging.basicConfig(level=logging.INFO)

    cert = open(os.path.expanduser(cfg.LND_CERT_PATH)).read()
    creds = grpc.ssl_channel_credentials(cert)
    channel = grpc.secure_channel('localhost:10009', creds)
    stub = lnrpc.LightningStub(channel)

    response = stub.WalletBalance(ln.WalletBalanceRequest(witness_only=True))
    print response.total_balance

    request = ln.GetInfoRequest()
    response = stub.GetInfo(request)
    print response

    db = LightningDB(cfg.DB_PATH)

    tweet = TweetClient(cfg.twitter, db, cfg.twitter_owner, ln)
    tweet.watch()

if __name__ == "__main__":
    main()