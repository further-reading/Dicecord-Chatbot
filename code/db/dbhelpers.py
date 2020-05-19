import sqlite3
import datetime


def connect(db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    return conn, cursor


def create_tables(db):
    conn, cursor = connect(db)
    query = """CREATE TABLE players (
  server INTEGER NOT NULL,
  channel INTEGER NOT NULL,
  player INTEGER,
  flavour TEXT,
  last_roll TEXT,
  PRIMARY KEY (server, channel, player)
);"""
    # prefix table creation will go here
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def get_flavour(message, db):
    conn, cursor = connect(db)
    # search table
    params = {
        'server': message.guild.id,
        'channel': message.channel.id,
        'player': message.author.id,
    }
    query = """SELECT flavour FROM players 
               WHERE server = :server AND
                     channel = :channel AND
                     player = :player"""
    cursor.execute(query, params)
    flavour = cursor.fetchone()
    update_last_roll(params, cursor, conn)
    cursor.close()
    conn.close()
    if flavour:
        return flavour[0]


def update_last_roll(params, cursor, conn):
    # db are not needed as it will always be updated when get_flavour runs
    now = datetime.datetime.now()
    params['now'] = now
    query = """UPDATE players SET last_roll=:now
               WHERE server = :server AND
                     channel = :channel AND
                     player = :player"""
    with conn:
        cursor.execute(query, params)


def clear_inactive_records(db):
    conn, cursor = connect(db)
    now = datetime.datetime.now()
    then = now - datetime.timedelta(days=30)
    query = """DELETE FROM players
               WHERE last_roll < :then"""
    with conn:
        cursor.execute(query, {'then': then})
    cursor.close()
    conn.close()


def get_prefix(message, db):
    # NYI
    pass