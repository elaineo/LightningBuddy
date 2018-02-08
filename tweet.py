from TwitterAPI import TwitterAPI
import json
import logging
import re

HUMAN_COMMANDS = ['CONNECT', 'GIVE', 'FUNDCHANNEL']
BOT_COMMANDS = ['GETINFO', 'GETINVOICE']

class Parsers:
    @staticmethod
    def extract_uri(msg):
        regex = re.compile('[0-9A-Fa-f]{66}@*[\d.]*:*\d*')
        uri = list(filter((lambda x: re.match(regex, x)), msg.split()))
        if len(uri) < 1:
            raise ValueError("Invalid URI: %s" % msg)
        return uri[0]

    @staticmethod
    def extract_amount(msg):
        # TODO: Parse currency units
        amount = re.findall('\d+|$', msg)
        if len(amount) < 1:
            raise ValueError("Invalid amount: %s" % msg)
        return amount[0]

    @staticmethod
    def extract_info(uri):
        peer_id, peer_address = uri.split("@")
        peer_ip, peer_port = peer_address.split(":")
        return peer_id, peer_ip, peer_port

    @staticmethod
    def extract_bolt11(msg):
        regex = re.compile('ln[0-9A-Za-z]+')
        bolt11 = list(filter((lambda x: re.match(regex, x)), msg.split()))
        if len(bolt11) < 1:
            raise ValueError("Invalid invoice: %s" % msg)
        return bolt11[0]

class TweetClient:
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

        if command.get('command') == "CONNECT":
            msg = '%s GETINFO' % reply_to
            status = 'data-req'
        elif command.get('command') == "GIVE":
            amount = Parsers.extract_amount(tweet)
            msg = '%s GETINVOICE %d' % (reply_to, amount)
            status = 'data-req'
        elif command.get('command') == "FUNDCHANNEL":
            peer_id = command.get('pubkey')
            msg = self.lnrpc._fundchannel(peer_id)
            status = 'complete'
        else:
            print("Command not found: %s" % command.get('command'))
            raise 
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

        # other user involved
        users = tweet.get('entities').get('user_mentions')
        user = [ u for u in users if u.get('id') != self.bot.get('id') ]
        user = None if len(user)==0 else user[0]

        # Check for owner instructions, counterparty
        if tweet.get('user').get('id') == self.owner.get('id'):
            for c in HUMAN_COMMANDS:
                if c in text:
                    return c, user, None
        # check for bot-to-bot instructions
        else:
            for c in BOT_COMMANDS:
                if c in text:
                    return c, None, tweet.get('user')

        return None, None, None

    def _record_new_command(self, command, sid, creator, peer, bot):
        assert bot or peer, "Neither peer nor bot found for %s" % command

        if not peer: 
            bot_uid = bot.get('id') 
            peer_db = self.db.peers.get_by_bot(bot_uid)
            peer_uid = None if not peer_db else peer_db.get('uid')
        else:
            peer_uid = peer.get('id')
            peer_db = self.db.peers.get_by_uid(peer_uid)
            bot_uid = None if not peer_db else peer_db.get('bot_uid')
            if not peer_db:
                peer_db = self.db.peers.new(peer_uid, peer.get('screen_name'))

        full = self.db.commands.new(sid, command, creator.get('id'), peer_uid, bot_uid) 
        full.update(peer_db)

        return full

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
            amount = Parsers.extract_amount(tweet)
            label = tweet
            msg = self.lnrpc.get_invoice(amount, label)
        sid = self._post(msg, command.get('last_sid'))
        # update status
        return self.db.commands.update_status(command.get('sid'), sid, 'complete')

    def _process_bot_response(self, command, tweet):
        if command.get('command') == "CONNECT":
            # Connect to new peer
            uri = Parsers.extract_uri(tweet)
            msg = self.lnrpc._connect(uri)
            pubkey, ip, port = Parsers.extract_info(uri)
            uid = command.get('peer_uid')
            self.db.peers.set_node(uid, pubkey, ip, port)
        elif command.get('command') == "GIVE":
            # Pay invoice
            # TODO: Validate invoice amount
            bolt11 = Parsers.extract_bolt11(tweet)
            pay_info = self.lnrpc.decodepay(bolt11)
            msg = self.lnrpc._pay(bolt11)
        elif command.get('command') == "FUNDCHANNEL":
            # args should be peer_id
            peer_id = command.get('pubkey')
            msg = self.lnrpc._fundchannel(peer_id)
        sid = self._post(msg, command.get('last_sid'))
        # update status
        return self.db.commands.update_status(command.get('sid'), sid, 'complete')

    def _resume_command(self, command, tweet):
        """ Continue executing an existing command, either from bot-req or data-req
        """
        logging.info(tweet)
        logging.info(command)
        owner = tweet.get('user')
        if command.get('status') == 'bot-req':
            # other user involved
            users = tweet.get('entities').get('user_mentions')
            user = [ u for u in users if u.get('id') != self.bot.get('id') ]
            bot = None if len(user)==0 else user[-1]
            if bot:
                self.db.peers.add_bot(owner.get('id'), bot.get('id'), bot.get('screen_name'))
                self.db.commands.update_status(command.get('last_sid'), tweet.get('id'), 'bot-ack')
                self._request_data(command)
            else:
                logging.error('Bot retrieval error')
        elif command.get('status') == 'data-req':
            # forward data to rpc
            return self._process_bot_response(command, tweet.get('text'))

    def watch(self):  
        """
        Filter tweets based on bot's screen name
        """
        msgs = self.api.request('statuses/filter', { 'track': self.bot.get('screen_name') })

        for m in msgs:
            logging.info(m)
            last_sid = m.get('in_reply_to_status_id')
            if last_sid:
                # Look up command
                command = self.db.commands.get_by_last_sid(last_sid)
                if not command:
                    continue
                # Check for correct user
                user = m.get('user').get('id')
                if user != command.get('peer_uid') and user != command.get('bot_uid'):
                    continue
                # Respond to command
                response = self._resume_command(command, m)
            else:
                tweet = m.get('text')
                sid = m.get('id_str')
                creator = m.get('user')
                command, peer, bot = self._filter(m)
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
       