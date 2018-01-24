
class Commands:
    """Issued commands and execution state. Each command has a creator (original command issuer), 
       owner (human counterparty), bot (owned by human counterparty), command.
       sid refers to Twitter Status ID

       Schema overview:
        | sid         |  command | creator_uid | peer_uid  | bot_uid   | last_sid  | status  | updated |
        +-------------+----------+-------------+-----------+-----------+-----------+---------+---------|
        | 66266839447 | CONNECT  | 738123385   | 738123385 | 873303322 | 955702923 |         |         |
        +-------------+----------+-------------+-----------+-----------+-----------+---------+---------|
    """

    fields = ['sid', 'command', 'creator_uid', 'peer_uid', 'bot_uid', 'last_sid', 'status', 'updated']

    def __init__(self, db):

        self.db = db
        self.db.execute([
            'CREATE TABLE IF NOT EXISTS commands (',
            '    sid INTEGER PRIMARY KEY, command VARCHAR,'
            '    creator_uid INTEGER, peer_uid INTEGER, bot_uid INTEGER,'
            '    last_sid INTEGER UNIQUE, status VARCHAR DEFAULT \'new\','
            '    updated DATETIME DEFAULT (STRFTIME(\'%s\',\'now\')) NOT NULL);'])

    def new(self, sid, command, creator_uid, peer_uid=None, bot_uid=None):
        """
        Add newly received command
        """
        self.db.execute([
            'INSERT OR REPLACE INTO commands (',
            '    sid, command, creator_uid, peer_uid, bot_uid, last_sid )', 
            '    VALUES (?, ?, ?, ?, ?, ?)'],  
                ( sid, command, creator_uid, peer_uid, bot_uid, sid )
            )

    def get_by_sid(self, sid):
        """
        Find command by originating status ID
        """
        rv = self.db.execute('SELECT * FROM commands WHERE sid=?', (sid, )).fetchone()
        if rv:
            return dict(zip(Commands.fields, rv))

        return None       

    def get_by_last_sid(self, sid):
        """
        Find command by most recent status ID 
        """
        rv = self.db.execute('SELECT * FROM commands WHERE last_sid=?', (sid, )).fetchone()
        if rv:
            return dict(zip(Commands.fields, rv))

        return None       

    def update_status(self, last_sid, new_sid, status):
        """
        Update command status based on status ID
        """
        self.db.execute(
            'UPDATE commands SET last_sid = ? , status = ? WHERE last_sid = ?',
            (new_sid, status, last_sid))

        return self.get_by_last_sid(new_sid)