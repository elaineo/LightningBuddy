from TwitterAPI import TwitterAPI
import json
import logging

HUMAN_COMMANDS = ['CONNECT', 'GIVE', 'FUNDCHANNEL']
BOT_COMMANDS = ['GETINFO', 'GETINVOICE']

class TweetClient:
    def __init__(self, config, db, owner):
        self.api = TwitterAPI(config['consumer_key'], config['consumer_secret'], 
            config['access_token'], config['access_token_secret'])
        self.db = db

        bot_id = config['access_token'].split('-')[0]
        bot_raw = self.api.request('users/lookup', {'user_id': bot_id})
        owner_raw = self.api.request('users/lookup', {'screen_name': owner})

        try:
            self.bot = json.loads(bot_raw.response.text)[0]
            self.owner = json.loads(owner_raw.response.text)[0]
        except KeyError:
            print("Cannot access Twitter account. Check API keys.")
            raise 

    def _post(self, msg, reply_sid):
        tweet = self.api.request('statuses/update', {'status': msg, 'in_reply_to_status_id': reply_sid })
        return tweet.get('id_str')

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

    def _record_new_command(self, sid, creator, command, peer, bot):
        assert bot or peer, "Neither peer nor bot found for %s" % command

        if not peer: 
            bot_uid = bot.get('id') 
            peer_db = self.db.peers.get_by_bot(bot_uid)
            peer_uid = None if not peer_db else peer_db.get('uid')
        else:
            peer_uid = peer.get('id')
            peer_db = self.db.peers.get_by_uid(peer_uid)

        full = self.db.commands.new(sid, command, creator.get('id'), peer_uid)

        return full.update(peer_db)

    def _execute_bot_response(self, command, args):
        logging.info(command)
        logging.info(args)

    def _execute_human_response(self, command, args):
        logging.info(command)
        logging.info(args)
        # TODO: Validate args
        
        # check for associated bot
        if not command.get('bot_uid'):
            self._request_bot(command)
        else: 
            reply_to = '@%s ' % command.get('bot_name')

            if command == "CONNECT":
                msg = '%s GETINFO' % reply_to
            elif command == "GIVE":
                msg = '%s GETINVOICE %d' % (reply_to, args)
            sid = self._post(msg, command.get('last_sid'))
            # update status

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
            tweet = m.get('text')
            logging.info(m)
            if m.get('in_reply_to_status_id'):
                response = self._resume_command(m)
                # Look up command
                # Respond to command
            else:
                sid = m.get('id_str')
                creator = m.get('user')
                command, peer, bot = self._filter(m)
                if not command:
                    continue
                # Record new command
                command_full = self._record_new_command(command, sid, creator, peer, bot)
                # Respond to command
                if command in BOT_COMMANDS:
                    self._execute_bot_response(command_full, tweet)
                else:
                    self._execute_human_response(command_full, tweet)
            continue
       