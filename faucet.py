"""
FaucetBot

Accept incoming connections, then respond by funding a channel.

OPENFAUCET
    GETINFO (data-req)
    CONNECT, FUNDCHANNEL
"""

from TwitterAPI import TwitterAPI
import json
import logging
import re

HUMAN_COMMANDS = ['OPENFAUCET']
BOT_COMMANDS = ['GETINFO', 'GETINVOICE', 'GETBALANCE']

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

    @staticmethod
    def extract_faucet(msg):
        amount = re.findall('\ \d+|$', msg)
        if len(amount) < 1:
            return None, None
        elif len(amount) == 1:
            return int(amount[0]), None
        else:
            return int(amount[0]), int(amount[1])

class FaucetClient:
    def __init__(self, config, db, owner, lnrpc):
        self.api = TwitterAPI(config['consumer_key'], config['consumer_secret'], 
            config['access_token'], config['access_token_secret'])
        self.db = db
        self.lnrpc = lnrpc

        bot_id = config['access_token'].split('-')[0]
        bot_raw = self.api.request('users/lookup', {'user_id': bot_id})
        owner_raw = self.api.request('users/lookup', {'screen_name': owner})

        try:
            self.bot = bot_raw.json()[0]
            logging.debug(self.bot)
            self.owner = owner_raw.json()[0]
            logging.debug(self.owner)
        except KeyError:
            print("Cannot access Twitter account. Check API keys.")
            raise 

    def _post(self, msg, reply_sid):
        tweet = self.api.request('statuses/update', 
            {'status': msg, 'in_reply_to_status_id': reply_sid, 'auto_populate_reply_metadata': True }).json()
        logging.info(tweet)
        return tweet.get('id_str')

    def _request_bot(self, command):
        reply_to = "@%s" % command.get('screen_name')
        msg = reply_to + " Please introduce me to your bot."
        sid = self._post(msg, command.get('last_sid'))
        return self.db.commands.update_status(command.get('sid'), sid, 'bot-req')

    def _request_data(self, command, tweet):
        # same as execute_human_response
        reply_to = "@%s" % command.get('bot_name')

        if command.get('command') == "OPENFAUCET":
            msg = '%s GETINFO' % reply_to
            status = 'data-req'
        else:
            raise ValueError("Command not found: %s" % command.get('command'))
        sid = self._post(msg, command.get('last_sid'))
        # update status
        return self.db.commands.update_status(command.get('sid'), sid, status)

    def _filter(self, tweet):
        """ Filter for new instructions from human owner or other bots
        """
        if tweet.get('retweet_count') > 0:
            return None, None, None

        text = tweet.get('text')
        if not text:
            return None, None, None
        text = text.upper()

        # Check for owner instructions, counterparty
        for c in HUMAN_COMMANDS:
            if c in text:
                return c, tweet.get('user'), None
        # check for bot-to-bot instructions
        for c in BOT_COMMANDS:
            if c in text:
                return c, None, tweet.get('user')

        return None, None, None

    def _record_new_command(self, command, sid, creator, peer, bot):
        assert bot or peer, "Neither peer nor bot found for %s" % command

        if not peer: 
            bot_uid = bot.get('id')
            peer_uid = None
            peer_db = None
        else:
            peer_uid = peer.get('id')
            peer_db = self.db.peers.get_by_uid(peer_uid)
            bot_uid = None if not peer_db else peer_db.get('bot_uid')
            if not peer_db:
                peer_db = self.db.peers.new(peer_uid, peer.get('screen_name'))

        full = self.db.commands.new(sid, command, creator.get('id'), peer_uid, bot_uid) 
        if peer_db:
            full.update(peer_db)

        return full

    def _get_full(self, sid):
        command = self.db.commands.get_by_sid(sid)
        if command.get('bot_uid'):
            peer = self.db.peers.get_by_bot(command.get('bot_uid'))
        else:
            peer = self.db.peers.get_by_uid(command.get('peer_uid'))
        command.update(peer)
        return command

    def _execute_human_response(self, command, tweet):
        # check for associated bot
        if not command.get('bot_uid'):
            return self._request_bot(command)
        else: 
            return self._request_data(command, tweet)

    def _execute_bot_response(self, command, tweet):
        if command.get('command') == "GETINFO":
            msg = self.lnrpc.get_uri()
        elif command.get('command') == "GETINVOICE":
            amount, description = Parsers.extract_payment(tweet)
            msg = self.lnrpc.get_invoice(amount, command.get('bot_name'), description)
        elif command.get('command') == "GETBALANCE":
            msg = self.lnrpc.get_balance()    
        sid = self._post(msg, command.get('last_sid'))
        # update status
        return self.db.commands.update_status(command.get('sid'), sid, 'complete')

    def _process_bot_response(self, command, tweet, orig=None):
        if command.get('command') == "OPENFAUCET":
            # Connect to new peer
            uri = Parsers.extract_uri(tweet)
            pubkey, ip, port = Parsers.extract_info(uri)
            msg = self.lnrpc._connect(pubkey, ip, port)
            uid = command.get('peer_uid')
            self.db.peers.set_node(uid, pubkey, ip, port)
            sid = self._post(msg, command.get('last_sid'))
            # Fund channel (commitment amount, initial balance)
            commitment, init_balance = Parsers.extract_faucet(orig) if orig else None, None

            msg = "%s\nDONE." % self.lnrpc.open_faucet(pubkey, commitment, init_balance)
            sid = self._post(msg, sid)
        # update status
        return self.db.commands.update_status(command.get('sid'), sid, 'complete')

    def _resume_command(self, command, tweet):
        """ Continue executing an existing command, either from bot-req or data-req
        """
        owner = tweet.get('user')
        text = tweet.get('extended_tweet').get('full_text') if tweet.get('truncated') else tweet.get('text')
        orig_raw = self.api.request('statuses/lookup', {'id': command.get('sid')})
        orig = orig_raw.json()[0]
        if command.get('status') == 'bot-req':
            # other user involved
            users = tweet.get('entities').get('user_mentions')
            user = [ u for u in users if u.get('id') != self.bot.get('id') ]
            bot = None if len(user)==0 else user[-1]
            if bot:
                self.db.peers.add_bot(owner.get('id'), bot.get('id'), bot.get('screen_name'))
                self.db.commands.update_bot(command.get('sid'), tweet.get('id'), bot.get('id'), 'bot-ack')
                command_full = self._get_full(command.get('sid'))
                self._request_data(command_full, text)
            else:
                logging.error('Bot retrieval error')
        elif command.get('status') == 'data-req':
            self.db.commands.update_status(command.get('sid'), tweet.get('id'), 'data-ack')
            command_full = self._get_full(command.get('sid'))
            # forward data to rpc
            return self._process_bot_response(command_full, text, orig.get('text'))

    def watch(self):  
        """
        Filter tweets based on bot's screen name
        """
        msgs = self.api.request('statuses/filter', { 'track': self.bot.get('screen_name') })

        for m in msgs:
            logging.info(m)
            last_sid = m.get('in_reply_to_status_id')
            command = self.db.commands.get_by_last_sid(last_sid) if last_sid else None
            if command:
                # Look up command
                logging.info(command)
                # Check for correct user
                user = m.get('user').get('id')
                if user != command.get('peer_uid') and user != command.get('bot_uid'):
                    continue
                # Respond to command
                r = self._resume_command(command, m)
                logging.info(r)
                continue
            tweet = m.get('extended_tweet').get('full_text') if m.get('truncated') else m.get('text')
            sid = m.get('id_str')
            creator = m.get('user')
            command, peer, bot = self._filter(m)
            logging.info('Command: %s, Peer: %s, Bot: %s' % (command, str(peer), str(bot)) )
            if not command:
                continue
            # Record new command
            command_full = self._record_new_command(command, sid, creator, peer, bot)
            # Respond to command
            if command in BOT_COMMANDS:
                r = self._execute_bot_response(command_full, tweet)
            else:
                r = self._execute_human_response(command_full, tweet)
            logging.info(r)
            continue
       