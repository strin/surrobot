# shared database utils.
import sqlite3 as sql

class DBConn(object):
    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, type, value, traceback):
        raise NotImplementedError()


