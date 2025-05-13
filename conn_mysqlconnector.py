# if u still prefer this

from flask import g
import mysql.connector
from mysql.connector import errors

def init():
  if "db" not in g:
    config = {
      'host': 'localhost',
      'port': 3306,
      'user': 'root',
      'password': 'root',
      'database': 'gcs',
    }

    try:
      g.db = mysql.connector.connect(**config)
    except errors.DatabaseError as e:
      if e.errno == 1273:  # Unknown collation error
        config['charset'] = 'utf8mb4'
        config['collation'] = 'utf8mb4_general_ci'
        g.db = mysql.connector.connect(**config)
      else:
        raise  # re-raise if not a collation error

  return g.db

def close():
  db = g.pop("db", None)
  if db is not None:
    db.close()
