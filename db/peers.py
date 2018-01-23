

class Peers:
    """Table of owner's peers. Schema overview:
        | uid         | screen_name | node_id | ip_addr       | port | channel_id   | connected |
        +-------------+-------------+---------+---------------+------+--------------+-----------|
        | 66266839447 | lightning   | 02a82...| 24.212.242.60 | 9735 | 1259839:32:1 | 1         |
        +-------------+-------------+---------+---------------+------+--------------+-----------|
    """

    fields = ['uid', 'screen_name', 'node_id', 'ip_addr', 'port', 'channel_id', 'connected']

    def __init__(self, db):

        self.db = db
        self.db.execute([
            'CREATE TABLE IF NOT EXISTS peers (',
            '    uid INTEGER PRIMARY KEY, screen_name VARCHAR UNIQUE, node_id VARCHAR, ip_addr VARCHAR,',
            '    port INTEGER, channel_id VARCHAR UNIQUE, connected INTEGER DEFAULT 0);'])

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

    def add_node(self, uid, screen_name, node_id=None, ip_addr=None, port=None):
        """
        Add new Twitter friend with node
        """
        self.db.execute([
            'INSERT OR REPLACE INTO peers (',
            '    uid, screen_name, node_id, ip_addr, port )', 
            '    VALUES (?, ?, ?, ?, ?)'],  
                ( uid, screen_name, node_id, ip_addr, port )
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

    def set_node(self, uid, node_id, ip_addr, port=None):
        """
        Add a node to twitter peer and return full mapping of keys, values
        """
        self.db.execute(
            'UPDATE peers SET node_id = ? , ip_addr = ?, port = ? WHERE uid = ?',
            (node_id, ip_addr, port, uid))

        return self.get_by_uid(uid)
