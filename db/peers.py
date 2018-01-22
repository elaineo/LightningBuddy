

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

    def add(self, p):
        """
        Add new peer to DB and return a mapping of fields and values
        """
        self.db.execute(
            'INSERT INTO peers (',
            '    uid, screen_name, node_id, ip_addr, port, channel_id, connected )', 
            '    VALUES (?, ?, ?, ?, ?, ?, ?)', ( 
                p["uid"], p["screen_name"], p["node_id"], p["ip_addr"], p["port"], 
                p["channel_id"], p["connected"])
            )

    def get_by_uid(self, uid):
        """
        Find twitter peer by uid
        """
        rv = self.db.execute('SELECT * FROM peers WHERE uid=?', (uid, )).fetchone()
        if rv:
            return rv[0]

        return None

    def get_by_name(self, name):
        """
        Find twitter peer by uid
        """
        rv = self.db.execute('SELECT * FROM peers WHERE screen_name=?', (name, )).fetchone()
        if rv:
            return rv[0]

        return None

    def set_node(self, uid, node):
        """
        Add a node to twitter peer
        """
        self.db.execute(
            'UPDATE peers SET node_id = ? , ip_addr = ?, port = ? WHERE uid = ?',
            (node["id"], node["ip"], node["port"], uid))
