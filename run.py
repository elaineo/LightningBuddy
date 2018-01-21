from lightning import LightningRpc
from TwitterAPI import TwitterAPI
import config as cfg

import os
import json
import logging

ln_path = os.environ['LN_PATH'] or os.path.join(os.environ['HOME'], '.lightning')
rpc_path = os.path.join(ln_path, '/lightning-rpc')

def main():
    ln = LightningRpc(rpc_path)
    bot = TwitterAPI(cfg.twitter['consumer_key'], cfg.twitter['consumer_secret'], 
        cfg.twitter['access_token'], cfg.twitter['access_token_secret'])

    # Get info about Lightning and initialize vars
    info = ln.getinfo()
    node_id = info['id']
    node_address = info['address'][0]['address']
    node_port = info['port']

