from lightning import LightningRpc
from TwitterAPI import TwitterAPI
import config as cfg

import os
import json
import logging

COMMANDS = ['CONNECT', 'FUNDCHANNEL', 'PAY', 'CLOSE']

class LightningWrapper(LightningRpc):
    """API for Lightning RPC client
    """
    def getinfo_(self):
        info = self.getinfo()
        node_id = info['id']
        node_address = info['address'][0]['address']
        node_port = info['port'] or 9735
        "%s@%s:%d" % (node_id, node_address, node_port)

    def connect(self, uri):
        # need to validate this
        peer_id, peer_address = uri.split("@")
        peer_ip, peer_port = peer_address.split(":")
        self.connect(peer_id, peer_ip, peer_port)

    def fundchannel(self, node_id, satoshis=cfg.CHANNEL_AMOUNT):
        self.fundchannel(node_id, satoshis)


if __name__ == "__main__":
    ln_path = os.getenv('LN_PATH') or os.path.join(os.getenv('HOME'), '.lightning')
    rpc_path = os.path.join(ln_path, '/lightning-rpc')
    logging.info(rpc_path)

    ln = LightningWrapper(LightningRpc(rpc_path))
    bot = TwitterAPI(cfg.twitter['consumer_key'], cfg.twitter['consumer_secret'], 
        cfg.twitter['access_token'], cfg.twitter['access_token_secret'])

    # Get info about Lightning node
    info = ln.getinfo_()
    logging.info(info)

    # Get info about twitter account
    account = bot.request('account/settings')
    bot_name = account['screen_name']
    owner = bot.request('users/lookup', {'screen_name': cfg.twitter_owner})
    owner_id = owner[0]['id_str']

    # Follow account owner, filter tweets based on bot's screen name
    msgs = bot.request('statuses/filter', {'follow':[owner_id], 'track':bot_name})

    for m in msgs:
        tweet = m.get('text')
        logging.debug(tweet)