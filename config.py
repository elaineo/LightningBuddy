#!/usr/bin/env python

# Twitter API keys
""" eiainebase
twitter = { 'consumer_key': 'evsykaFvVe7wjUYOQY7e2Zldg',
            'consumer_secret': 'YKDuD10Jgb5nHMSy5bCmmZ8ejCUNZF0IiDNZcZ4yBV7ER3Q8h3',
            'access_token': '738123385440346112-ocQGoFLeKJXdOAVhhPW9DG31svkytH4',
            'access_token_secret': 'pZ6QUL3maZcLUyecYNE75SePlolJtHB2mD28FoUPNYhSf' }
"""
""" kompilerbot"""
twitter = { 'consumer_key': 'FVKmhOaiBcZ5phfe2fXC5lKvd',
            'consumer_secret': 'WFozIrUABinXZI199Jd4PmRpfD12ENNoIC4JgqXaVK9IMvvSIM',
            'access_token': '732074802794487808-BNeQcnbbFK5i5gU5q5d9ni6YLwE0MWV',
            'access_token_secret': 'EUCTRWmHamxbmW8KionEPsMuVjKccUAjkqwJ8mwu5xmjW' }

""" faucetbot
twitter = { 'consumer_key': 'IXghI9F2bQlilIHsE5vXz25pI',
            'consumer_secret': 'WaizcYStClzENTvraGQvDYPI568CuL4adK8sgpXZSBtikYiKXG',
            'access_token': '955199941105758208-9SmTzVRUxC7I7XNKwB9XXMjcc0JNww6',
            'access_token_secret': 'U9RoTUxhOco5772DpxEevFd8ubIAhmYSL72XxvgAfM8Qg' }
"""
twitter_owner = 'george_the_egg'

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
LND_CERT_PATH = '~/Library/Application Support/Lnd/tls.cert'
LND_HOST = 'localhost:10009'
NODE_ADDRESS = '107.128.213.29'
NODE_PORT = 49725
