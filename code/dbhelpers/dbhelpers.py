import sqlite3 as db
import datetime


def connect(dbpath):
    conn = db.connect(dbpath)
    cursor = conn.cursor()
    return conn, cursor


def create_tables(dbpath):
    conn, cursor = connect(dbpath)
    query1 = """CREATE TABLE IF NOT EXISTS players (
  server INTEGER NOT NULL,
  channel INTEGER NOT NULL,
  player INTEGER,
  flavour INTEGER DEFAULT 1,
  splat TEXT DEFAULT 'default',
  last_roll TEXT,
  PRIMARY KEY (server, channel, player)
);"""
    cursor.execute(query1)
    conn.commit()
    cursor.close()
    conn.close()

    conn, cursor = connect(dbpath)
    query2 = """CREATE TABLE IF NOT EXISTS prefixes (
  server INTEGER NOT NULL,
  channel INTEGER NOT NULL,
  prefix TEXT DEFAULT '@mention',
  PRIMARY KEY (server, channel)
);"""
    cursor.execute(query2)
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
    if level == 'user':
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
    conn, cursor = connect(dbpath)
    params = {
        'server': message.guild.id,
        'channel': message.channel.id,
    }

    query = """SELECT prefix FROM prefixes
               WHERE server = :server AND
                     (channel = :channel OR channel = 0)
               ORDER BY channel DESC;"""

    cursor.execute(query, params)
    prefix = cursor.fetchone()
    if prefix:
        prefix = prefix[0]

    cursor.close()
    conn.close()

    return prefix


def set_prefix(prefix, message, dbpath, server_wide=False):
    conn, cursor = connect(dbpath)
    params = {
        'server': message.guild.id,
    }
    if server_wide:
        params['channel'] = 0
    else:
        params['channel'] = message.channel.id

    if prefix:
        params['prefix'] = prefix
        query = """REPLACE INTO prefixes
                   VALUES (:server, :channel, :prefix);"""

    else:
        query = """DELETE FROM prefixes
                   WHERE server = :server AND 
                         channel = :channel;"""

    cursor.execute(query, params)
    cursor.close()
    conn.commit()
    conn.close()
