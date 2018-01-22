

class Peers:
    """Table of owner's peers. Schema overview:
        | uid         | screen_name | node_id | ip_addr       | port | channel_id   | connected |
        +-------------+-------------+---------+---------------+------+--------------+-----------|
        | 66266839447 | lightning   | 02a82...| 24.212.242.60 | 9735 | 1259839:32:1 | 1         |
        +-------------+-------------+---------+---------------+------+--------------+-----------|
    The tuple (uid, channel_id) is unique
    """

    fields = ['uid', 'screen_name', 'node_id', 'ip_addr', 'port', 'channel_id', 'connected']

    def __init__(self, db):

        self.db = db
        self.db.execute([
            'CREATE TABLE IF NOT EXISTS peers (',
            '    uid INTEGER PRIMARY KEY, screen_name VARCHAR, node_id VARCHAR, ip_addr VARCHAR,',
            '    port INTEGER, channel_id VARCHAR UNIQUE, connected INTEGER DEFAULT 0);'])

    def add(self, uid, p):
        """
        Add new peer to DB and return a mapping of fields and values
        """
