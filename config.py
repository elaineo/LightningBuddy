#!/usr/bin/env python

twitter = { 'consumer_key': 'uMjpu9KEIb4pzJczrzfRydKBB',
            'consumer_secret': 'RNJPUIHnoUv4jWyW3RqERyWXURHjvpywfT1S4d4qByVl9q7Gh8',
            'access_token': '738199054430044161-5Pe4pZgEuEfjfAvS1KluFuJBC3SOxUW',
            'access_token_secret': 'iglmz4juz1SUvQ6fdveYcptPmaYIb0Vp5IG6qEsww9PbT' }

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
LND_CERT_PATH = '~/.lnd/tls.cert''
LND_HOST = 'localhost:10009'
NODE_ADDRESS = '45.76.235.75'
NODE_PORT = 9735
