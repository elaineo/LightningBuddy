import logging
import sys
sys.path.insert(0, 'googleapis')

import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import grpc

from google.protobuf.json_format import MessageToJson


class LndWrapper:
    """API for Lightning gRPC client
    """
    def __init__(self, cert, config):
        creds = grpc.ssl_channel_credentials(cert)
        channel = grpc.secure_channel(config.LND_HOST, creds)
        self.stub = lnrpc.LightningStub(channel)
        self.node_address = config.NODE_ADDRESS
        self.node_port = config.NODE_PORT
        self.channel_amount = config.CHANNEL_AMOUNT

    def get_uri(self):
        try:
            request = ln.GetInfoRequest()
            response = self.stub.GetInfo(request)
            logging.info(response)
            node_id = response.identity_pubkey
            return "%s@%s:%d" % (node_id, self.node_address, self.node_port)
        except grpc.RpcError as e:
           logging.error(e)
           return e.details()

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
           return e.details()

    def decodepay(self, bolt11):
        try:
            request = ln.PayReqString(
                pay_req=bolt11
            )
            response = self.stub.DecodePayReq(request)
            logging.info(response)
        except grpc.RpcError as e:
           logging.error(e)

    def _pay(self, bolt11):
        try:
            request = ln.SendRequest(
                payment_request=bolt11
            )
            response = self.stub.SendPaymentSync(request)
            logging.info(response)
            if response.payment_preimage:
                return "Preimage %s" % MessageToJson(response.payment_preimage)
            else:
                return str(response)
        except grpc.RpcError as e:
           logging.error(e)
           return e.details()

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
           return e.details()

    def _fundchannel(self, node_id, satoshis=None):
        try:
            request = ln.OpenChannelRequest(
                node_pubkey_string=node_id,
                local_funding_amount=satoshis or self.channel_amount
            )
            response = self.stub.OpenChannelSync(request)
            logging.info(response)
            if response.funding_txid_str:
                return response.funding_txid_str
            else:
                return MessageToJson(response) 
        except grpc.RpcError as e:
           logging.error(e)
           return e.details()
           