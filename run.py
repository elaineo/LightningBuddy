from lightning import LightningRpc
from tweet import TweetClient
import config as cfg

from db import LightningDB
import os
import json
import logging

class LightningWrapper(LightningRpc):
    """API for Lightning RPC client
    """
    def get_uri(self):
        info = self.getinfo()
        node_id = info['id']
        node_address = info['address'][0]['address']
        node_port = info['port'] or 9735
        return "%s@%s:%d" % (node_id, node_address, node_port)

    def get_invoice(self, amount):
        return self.invoice(amount, "lbl{}".format(random.random()), "twitter")

    def _connect(self, uri):
        # need to validate this
        peer_id, peer_address = uri.split("@")
        peer_ip, peer_port = peer_address.split(":")
        self.connect(peer_id, peer_ip, peer_port)

    def _fundchannel(self, node_id, satoshis=cfg.CHANNEL_AMOUNT):
        self.fundchannel(node_id, satoshis)


def main():
    logging.basicConfig(level=logging.INFO)

    ln_path = os.getenv('LN_PATH') or os.path.join(os.getenv('HOME'), '.lightning')
    rpc_path = os.path.join(ln_path, 'lightning-rpc')
    logging.info(rpc_path)

    ln = LightningWrapper(rpc_path)
    # Get URI for Lightning node
    # uri = ln.get_uri()
    # logging.info(uri)

    db = LightningDB(cfg.DB_PATH)

    tweet = TweetClient(cfg.twitter, db, cfg.twitter_owner, ln)
    tweet.watch()

if __name__ == "__main__":
    main()