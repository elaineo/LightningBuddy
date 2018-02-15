from lightning import LightningRpc
import logging
import random

class LightningWrapper(LightningRpc):
    """API for Lightning RPC client
    """
    def __init__(self, config):
        super( LightningWrapper, self ).__init__()
        self.channel_amount = config.CHANNEL_AMOUNT

    def get_uri(self):
        try:
            info = self.getinfo()
            node_id = info['id']
            node_address = info['address'][0]['address']
            node_port = info['port'] or 9735
            return "%s@%s:%d" % (node_id, node_address, node_port)
        except ValueError as e:
           logging.error(e)

    def get_invoice(self, amount, label, description=None):
        try:
            invoice = self.invoice(amount, "%s%s" % (label, str(random.randrange(999999))), description)
            return invoice['bolt11']
        except ValueError as e:
           logging.error(e)

    def _pay(self, bolt11):
        try:
            pay = self.pay(bolt11)
            return pay['preimage']
        except ValueError as e:
           logging.error(e)

    def _connect(self, node_id, host=None, port=None):
        try:
           connected = self.connect(peer_id, peer_ip, peer_port)
           return "Connected %s" + connected['id']
        except ValueError as e:
           logging.error(e)

    def _fundchannel(self, node_id, satoshis=None):
        try:
            tx = self.fundchannel(node_id, satoshis or self.channel_amount)
            return tx['funding_txid']
        except ValueError as e:
           logging.error(e)