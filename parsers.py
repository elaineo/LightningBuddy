import re

class Parsers:
    @staticmethod
    def extract_uri(msg):
        regex = re.compile('[0-9A-Fa-f]{66}@*[\d.]*:*\d*')
        uri = list(filter((lambda x: re.match(regex, x)), msg.split()))
        if len(uri) < 1:
            raise ValueError("Invalid URI: %s" % msg)
        return uri[0]

    @staticmethod
    def extract_payment(msg):
        # TODO: Parse currency units
        amount = re.findall('\ \d+|$', msg)
        if len(amount) < 1:
            raise ValueError("Invalid amount: %s" % msg)
        description = msg.split(amount[0], 1)[-1]
        return int(amount[0]), description

    @staticmethod
    def extract_info(uri):
        info = uri.split("@")
        peer_id = info[0]
        address = info[1].split(":") if len(info) > 1 else None
        peer_ip = address[0] if address else None
        peer_port = address[1] if address and len(address) > 1 else None 
        return peer_id, peer_ip, peer_port

    @staticmethod
    def extract_bolt11(msg):
        regex = re.compile('ln[0-9A-Za-z]+')
        bolt11 = list(filter((lambda x: re.match(regex, x)), msg.split()))
        if len(bolt11) < 1:
            raise ValueError("Invalid invoice: %s" % msg)
        return bolt11[0]