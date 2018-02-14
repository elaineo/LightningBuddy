#!/usr/bin/env python

# Twitter API keys (for LightningBuddy)
twitter = { 'consumer_key': '',
            'consumer_secret': '',
            'access_token': '',
            'access_token_secret': '' }

# Username of LightningBuddy's owner
twitter_owner = 'Elaine0u'

## Default Channel creation parameters
CHANNEL_AMOUNT = 100000  # in satoshis

DB_PATH = 'sqlite.db'

"""
Required for c-Lightning
"""
LN_PATH = '/root/.lightning'

"""
Required for LND
"""
# Lnd cert is at ~/.lnd/tls.cert on Linux and
# ~/Library/Application Support/Lnd/tls.cert on Mac
LND_CERT_PATH = '~/.lnd/tls.cert'
LND_HOST = 'localhost:10009'
NODE_ADDRESS = ''
NODE_PORT = 9735
