from tweet import TweetClient
import config as cfg

from db import LightningDB
from lndrpc import LndWrapper
from lightningrpc import LightningWrapper
from sys import argv
import os
import logging

def main():
    logging.basicConfig(level=logging.INFO)

    if len(argv) > 1 and argv[1]=='--clightning':
        ln_path = cfg.LN_PATH or os.path.join(os.getenv('HOME'), '.lightning')
        rpc_path = os.path.join(ln_path, 'lightning-rpc')
        logging.debug(rpc_path)

        ln = LightningWrapper(rpc_path)
    else:
        cert = open(os.path.expanduser(cfg.LND_CERT_PATH)).read()
        ln = LndWrapper(cert, cfg)

    db = LightningDB(cfg.DB_PATH)

    tweet = TweetClient(cfg.twitter, db, cfg.twitter_owner, ln)
    tweet.watch()

if __name__ == "__main__":
    main()