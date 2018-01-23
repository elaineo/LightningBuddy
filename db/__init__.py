import sqlite3
import logging
import os

from db.peers import Peers
from db.commands import Commands

class LightningDB:
    """DB-dependent wrapper around SQLite3.
    Runs migration if `user_version` is older than `MAX_VERSION` and register
    a trigger for automated orphan removal.
    """

    MAX_VERSION = 1

    def __init__(self, path):

        self.path = os.path.expanduser(path)

        rv = self.execute([
            "SELECT name FROM sqlite_master"
            "   WHERE type='table' AND name IN ('peers', 'commands')"]
        ).fetchone()

        self.peers = Peers(self)
        self.commands = Commands(self)

        if rv is None:
            self.execute("PRAGMA user_version = %i" % LightningDB.MAX_VERSION)
        else:
            self.migrate(to=LightningDB.MAX_VERSION)

        self.execute([
            'CREATE TRIGGER IF NOT EXISTS update_peers_timestamp',
            '    AFTER UPDATE ON peers',
            '    FOR EACH ROW',
            '    WHEN NEW.updated < OLD.updated',
            'BEGIN',
            '    UPDATE peers SET updated=(STRFTIME("%s","now")) WHERE uid=NEW.uid;',
            'END'])

        self.execute([
            'CREATE TRIGGER IF NOT EXISTS update_commands_timestamp',
            '    AFTER UPDATE ON commands',
            '    FOR EACH ROW',
            '    WHEN NEW.updated < OLD.updated',
            'BEGIN',
            '    UPDATE commands SET updated=(STRFTIME("%s","now")) WHERE sid=NEW.sid;',
            'END'])

    def execute(self, sql, args=()):

        if isinstance(sql, (list, tuple)):
            sql = ' '.join(sql)

        with sqlite3.connect(self.path) as con:
            return con.execute(sql, args)

    @property
    def version(self):
        return self.execute("PRAGMA user_version").fetchone()[0]

    def migrate(self, to):

        if self.version >= to:
            return

        logging.info("migrate database from version %i to %i", self.version, to)

        if self.version == 0:

            with sqlite3.connect(self.path) as con:
                con.execute('PRAGMA user_version = 1')

