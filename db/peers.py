
def Peer(uid, screen_name, bot_uid, bot_name):
    return {
        "peer_uid": uid,
        "screen_name": screen_name,
        "bot_uid": bot_uid,
        "bot_name": bot_name
    }

class Peers:
    """Table of owner's peers. Owner is presumably human. Bots can be shared, as can nodes (for now). 

       Schema overview:
        | uid (owner) | screen_name | bot_uid   | bot_name | pubkey  | ip_addr       | port | updated |
        +-------------+-------------+-----------+----------+---------+---------------+------+---------|
        | 66266839447 | lightning   | 214123433 | lnb0t    | 02a82...| 24.212.242.60 | 9735 |         |
        +-------------+-------------+-----------+----------+---------+---------------+------+---------|
    """

    fields = ['uid', 'screen_name', 'bot_uid', 'bot_name', 'pubkey', 'ip_addr', 'port', 'updated']

    def __init__(self, db):

        self.db = db
        self.db.execute([
            'CREATE TABLE IF NOT EXISTS peers (',
            '    uid INTEGER PRIMARY KEY, screen_name VARCHAR UNIQUE, bot_uid VARCHAR,'
            '    bot_name VARCHAR, pubkey VARCHAR, ip_addr VARCHAR, port INTEGER,'
            '    updated DATETIME DEFAULT (STRFTIME(\'%s\',\'now\')) NOT NULL);'])

    def __getitem__(self, uid):
        return Peer(*self.db.execute(
            "SELECT uid, screen_name, bot_uid, bot_name FROM peers WHERE uid=?", (uid, )).fetchone())

    def new(self, uid, screen_name):
        """
        Add new Twitter friend
        """
        self.db.execute([
            'INSERT OR REPLACE INTO peers (',
            '    uid, screen_name )', 
            '    VALUES (?, ?)'],  
                ( uid, screen_name )
            )
        return self[uid]

    def add_bot(self, uid, bot_uid, bot_name):
        """
        Add bot to Twitter friend
        """
        self.db.execute([
            'INSERT OR REPLACE INTO peers (',
            '    uid, bot_uid, bot_name )', 
            '    VALUES (?, ?, ?)'],  
                ( uid, bot_uid, bot_name )
            )

        return self.get_by_uid(uid)

    def add_node(self, uid, screen_name, pubkey=None, ip_addr=None, port=None):
        """
        Add new Twitter friend with node
        """
        self.db.execute([
            'INSERT OR REPLACE INTO peers (',
            '    uid, screen_name, pubkey, ip_addr, port )', 
            '    VALUES (?, ?, ?, ?, ?)'],  
                ( uid, screen_name, pubkey, ip_addr, port )
            )

        return self.get_by_uid(uid)

    def get_by_uid(self, uid):
        """
        Find twitter peer by uid
        """
        rv = self.db.execute('SELECT * FROM peers WHERE uid=?', (uid, )).fetchone()
        if rv:
            return dict(zip(Peers.fields, rv))

        return None

    def get_by_name(self, name):
        """
        Find twitter peer by name
        """
        rv = self.db.execute('SELECT * FROM peers WHERE screen_name=?', (name, )).fetchone()
        if rv:
            return dict(zip(Peers.fields, rv))

        return None

    def get_by_bot(self, bot_uid):
        """
        Find twitter peer by bot
        """
        rv = self.db.execute('SELECT * FROM peers WHERE bot_uid=?', (bot_uid, )).fetchone()
        if rv:
            return dict(zip(Peers.fields, rv))

        return None        

    def set_node(self, uid, pubkey, ip_addr, port=None):
        """
        Add a node to twitter peer and return full mapping of keys, values
        """
        self.db.execute(
            'UPDATE peers SET pubkey = ? , ip_addr = ?, port = ? WHERE uid = ?',
            (pubkey, ip_addr, port, uid))

        return self.get_by_uid(uid)
