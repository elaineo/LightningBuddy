from lightning import LightningRpc
from tweet import TweetClient
import config as cfg

from db import LightningDB
import os
import json
import random
import logging

class LightningWrapper(LightningRpc):
    """API for Lightning RPC client
    """
    def get_uri(self):
        try:
            info = self.getinfo()
            node_id = info['id']
            node_address = info['address'][0]['address']
            node_port = info['port'] or 9735
            return "%s@%s:%d" % (node_id, node_address, node_port)
        except ValueError, e:
           logging.error(e)

    def get_invoice(self, amount, label, description=None):
        try:
            invoice = self.invoice(amount, "%s%s" % (label, str(random.randrange(999999))), description)
            return invoice['bolt11']
        except ValueError, e:
           logging.error(e)

    def _pay(self, bolt11):
        try:
            pay = self.pay(bolt11)
            return pay['preimage']
        except ValueError, e:
           logging.error(e)

    def _connect(self, node_id, host=None, port=None):
        try:
           connected = self.connect(peer_id, peer_ip, peer_port)
           return "Connected %s" + connected['id']
        except ValueError, e:
           logging.error(e)

    def _fundchannel(self, node_id, satoshis=cfg.CHANNEL_AMOUNT):
        try:
            tx = self.fundchannel(node_id, satoshis)
            return tx['funding_txid']
        except ValueError, e:
           logging.error(e)
        


def main():
    logging.basicConfig(level=logging.INFO)

    ln_path = os.getenv('LN_PATH') or os.path.join(os.getenv('HOME'), '.lightning')
    rpc_path = os.path.join(ln_path, 'lightning-rpc')
    logging.debug(rpc_path)

    ln = LightningWrapper(rpc_path)

    db = LightningDB(cfg.DB_PATH)

    tweet = TweetClient(cfg.twitter, db, cfg.twitter_owner, ln)
    tweet.watch()

if __name__ == "__main__":
    main()