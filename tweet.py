from TwitterAPI import TwitterAPI
import json
import logging

HUMAN_COMMANDS = ['CONNECT', 'GIVE']
BOT_COMMANDS = ['GETINFO', 'FUNDCHANNEL', 'PAY_INVOICE', 'INVOICE']

class TweetClient:
    def __init__(self, config, owner):
        self.api = TwitterAPI(config['consumer_key'], config['consumer_secret'], 
            config['access_token'], config['access_token_secret'])

        bot_id = config['access_token'].split('-')[0]
        bot_raw = self.api.request('users/lookup', {'user_id': bot_id})
        self.bot = json.loads(bot_raw.response.text)[0]

        owner_raw = self.api.request('users/lookup', {'screen_name': owner})
        self.owner = json.loads(owner_raw.response.text)[0]

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
                    return c, user, tweet.get('user')

        return None, None, None

    def _response_status(self, tweet, command):
        """ Continue executing an existing command
            if tweet.get('in_reply_to_status_id')
        """
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
                response = self._response_status
            else:
                command, counterparty, commander = self._filter(m)
                logging.info(command)
                logging.info(counterparty)
                logging.info(commander)
       