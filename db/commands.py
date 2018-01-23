
class Commands:
    """Issued commands and execution state. Each command has a creator (original command issuer), 
       owner (human counterparty), bot (owned by human counterparty), command.
       sid refers to Twitter Status ID

       Schema overview:
        | sid         | creator_uid | owner_uid | bot_uid   | command  | last_sid  | status  | updated |
        +-------------+-------------+-----------+-----------+----------+-----------+---------+---------|
        | 66266839447 | 738123385   | 738123385 | 873303322 | CONNECT  | 955702923 |         |         |
        +-------------+-------------+-----------+-----------+----------+-----------+---------+---------|
    """

    fields = ['sid', 'creator_uid', 'owner_uid', 'bot_uid', 'command', 'last_sid', 'status', 'updated']

    def __init__(self, db):

        self.db = db
        self.db.execute([
            'CREATE TABLE IF NOT EXISTS commands (',
            '    sid INTEGER PRIMARY KEY, creator_uid INTEGER, owner_uid INTEGER,'
            '    bot_uid INTEGER, command VARCHAR, last_sid INTEGER UNIQUE, status VARCHAR,'
            '    updated DATETIME DEFAULT (STRFTIME(\'%s\',\'now\')) NOT NULL);'])    