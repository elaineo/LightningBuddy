from TwitterAPI import TwitterAPI
import json
import logging

HUMAN_COMMANDS = ['CONNECT', 'GIVE', 'FUNDCHANNEL']
BOT_COMMANDS = ['GETINFO', 'GETINVOICE']

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
        tweet = self.api.request('statuses/update', {'status': msg, 'in_reply_to_status_id': reply_sid }).json()
        return tweet.get('id_str')

    def _request_bot(self, command):
        reply_to = "@%s" % command.get('screen_name')
        msg = reply_to + " Please introduce me to your bot."
        return self._post(msg, command.get('last_sid'))

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
            bot_uid = peer_db.get('bot_uid')

        full = self.db.commands.new(sid, command, creator.get('id'), peer_uid, bot_uid)
        if peer_db:
            full.update(peer_db)

        return full

    def _execute_human_response(self, command, args):
        logging.info("Command: %s" % str(command))
        logging.info("Args: %s" % str(args))
        # TODO: Validate args
        
        # check for associated bot
        if not command.get('bot_uid'):
            sid = self._request_bot(command)
            return self.db.commands.update_status(command.get('sid'), sid, 'bot-req')
        else: 
            reply_to = '@%s ' % command.get('bot_name')

            if command == "CONNECT":
                msg = '%s GETINFO' % reply_to
            elif command == "GIVE":
                msg = '%s GETINVOICE %d' % (reply_to, args)
            sid = self._post(msg, command.get('last_sid'))
            # update status
            return self.db.commands.update_status(command.get('sid'), sid, 'data-req')

    def _execute_bot_response(self, command, args):
        logging.info("Command: %s" % str(command))
        logging.info("Args: %s" % str(args))

        if command.get('command') == "GETINFO":
            msg = self.lnrpc.get_uri()
        elif command.get('command') == "GETINVOICE":
            msg = self.lnrpc.get_uri(args)
        sid = self._post(msg, command.get('last_sid'))
        # update status
        return self.db.commands.update_status(command.get('sid'), sid, 'complete')

    def _resume_command(self, tweet, command):
        """ Continue executing an existing command
            if tweet.get('in_reply_to_status_id')
        """
        # check for correct user
        logging.info(tweet)

    def watch(self):  #callback functions for get_uri, fundchannel?, pay, invoice
        """
        Filter tweets based on bot's screen name
        """
        msgs = self.api.request('statuses/filter', { 'track': self.bot.get('screen_name') })

        for m in msgs:
            logging.info(m)
            last_sid = m.get('in_reply_to_status_id')
            if last_sid:
                command = self.db.commands.get_by_last_sid(last_sid)
                if not command:
                    continue
                response = self._resume_command(command, m)
                # Look up command
                # Respond to command
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
       