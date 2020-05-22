import sqlite3 as db
import datetime


def connect(dbpath):
    conn = db.connect(dbpath)
    cursor = conn.cursor()
    return conn, cursor


def create_tables(dbpath):
    conn, cursor = connect(dbpath)
    query = """CREATE TABLE players (
  server INTEGER NOT NULL,
  channel INTEGER NOT NULL,
  player INTEGER,
  flavour INTEGER DEFAULT 1,
  splat TEXT,
  last_roll TEXT,
  PRIMARY KEY (server, channel, player)
);"""
    # prefix table creation will go here
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()


def get_flavour(message, dbpath):
    conn, cursor = connect(dbpath)
    # search table
    params = {
        'server': message.guild.id,
        'channel': message.channel.id,
        'player': message.author.id,
    }
    update_last_roll(params, cursor, conn)
    query = """SELECT flavour, splat FROM players 
               WHERE server = :server AND
                     channel = :channel AND
                     player = :player"""
    cursor.execute(query, params)
    details = cursor.fetchone()
    cursor.close()
    conn.close()
    return details


def update_last_roll(params, cursor, conn):
    # db are not needed as it will always be updated when get_flavour runs
    now = datetime.datetime.now()
    params['now'] = now
    query = """UPDATE players SET last_roll=:now
               WHERE server = :server AND
                     channel = :channel AND
                     player = :player"""
    cursor.execute(query, params)
    if not cursor.rowcount:
        # entry not in table yet
        query = """INSERT INTO players (server, channel, player, last_roll) 
                       VALUES (:server, :channel, :player, :now)"""
        cursor.execute(query, params)

    conn.commit()



def clear_inactive_records(dbpath):
    conn, cursor = connect(dbpath)
    now = datetime.datetime.now()
    then = now - datetime.timedelta(days=30)
    query = """DELETE FROM players
               WHERE last_roll < :then"""
    with conn:
        cursor.execute(query, {'then': then})
    cursor.close()
    conn.close()


def set_flavour(message, setting, dbpath):
    if setting == 'on':
        setting = 1
    else:
        setting = 0

    conn, cursor = connect(dbpath)
    query = """UPDATE players
               SET flavour = :setting
               WHERE server = :server AND
                     channel = :channel AND
                     player = :player"""
    params = {
        'setting': setting,
        'server': message.guild.id,
        'channel': message.channel.id,
        'player': message.author.id,
    }
    update_last_roll(params, cursor, conn)
    with conn:
        cursor.execute(query, params)
    cursor.close()
    conn.close()


def set_splat(message, setting, dbpath):
    if setting == 'remove':
        setting = None
    conn, cursor = connect(dbpath)
    query = """UPDATE players
                   SET splat = :setting
                   WHERE server = :server AND
                         channel = :channel AND
                         player = :player"""
    params = {
        'setting': setting,
        'server': message.guild.id,
        'channel': message.channel.id,
        'player': message.author.id,
    }
    update_last_roll(params, cursor, conn)
    with conn:
        cursor.execute(query, params)
    cursor.close()
    conn.close()


def delete_content(message, level, dbpath):
    conn, cursor = connect(dbpath)
    if level == 'player':
        query = """DELETE FROM players
                           WHERE server = :server AND
                                 channel = :channel AND
                                 player = :player"""
    elif level == 'channel':
        query = """DELETE FROM players
                           WHERE server = :server AND
                                 channel = :channel"""
    elif level == 'server':
        query = """DELETE FROM players
                            WHERE server = :server"""

    params = {
        'server': message.guild.id,
        'channel': message.channel.id,
        'player': message.author.id,
    }
    with conn:
        cursor.execute(query, params)
    cursor.close()
    conn.close()


def get_prefix(message, dbpath):
    # NYI
    pass