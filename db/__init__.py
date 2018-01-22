import sqlite3
import logging
import os

from peers import Peers

class LightningDB:
    """DB-dependent wrapper around SQLite3.
    Runs migration if `user_version` is older than `MAX_VERSION` and register
    a trigger for automated orphan removal.
    """

    MAX_VERSION = 1

    def __init__(self, path, conf):

        self.path = os.path.expanduser(path)
        self.conf = conf

        rv = self.execute([
            "SELECT name FROM sqlite"
            "   WHERE type='table' AND name IN ('peers')"]
        ).fetchone()

        self.peers = Peers(self)

        if rv is None:
            self.execute("PRAGMA user_version = %i" % LightningDB.MAX_VERSION)
        else:
            self.migrate(to=LightningDB.MAX_VERSION)

        self.execute([
            'CREATE TRIGGER IF NOT EXISTS remove_stale_threads',
            'AFTER DELETE ON comments',
            'BEGIN',
            '    DELETE FROM threads WHERE id NOT IN (SELECT tid FROM comments);',
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

