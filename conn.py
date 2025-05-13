from flask import g
import pymysql

class DB:
    def __init__(self, conn):
        self.conn = conn

    def cursor(self, dictionary=False):
        return self.conn.cursor(pymysql.cursors.DictCursor) if dictionary else self.conn.cursor()

    def __getattr__(self, name):
        return getattr(self.conn, name)

def init():
    if "db" not in g:
        config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': 'root',
            'database': 'gcs',
            'charset': 'utf8mb4'
        }

        g.db = DB(pymysql.connect(**config))

    return g.db

def close():
    db = g.pop("db", None)
    if db is not None:
        db.close()
