import pytest
from dbhelpers import dbhelpers
import os
from unittest.mock import MagicMock, patch
import datetime


@pytest.fixture
def dbpath():
    try:
        os.remove('test.db')
    except:
        pass
    dbpath = 'test.db'
    dbhelpers.create_tables(dbpath='test.db')
    yield dbpath
    os.remove(dbpath)


def test_get_flavour(dbpath):
    # Arrange
    expected = (1, 'mage')
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO players (server, channel, player, flavour, splat)
               VALUES (10, 11, 12, 1, 'mage')"""
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12

    # Act
    actual = dbhelpers.get_flavour(message, dbpath)
    # Assert
    assert expected == actual


def test_get_flavour_default(dbpath):
    # Arrange
    expected = (1, 'default')

    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12

    # Act
    actual = dbhelpers.get_flavour(message, dbpath)
    # Assert
    assert expected == actual


@patch('dbhelpers.dbhelpers.datetime')
def test_get_flavour_update_last_roll(mock_datetime, dbpath):
    # Arrange
    #  Insert data to fake db
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO players (server, channel, player, last_roll)
                       VALUES (10, 11, 12, '2020-04-01 12:34:56')"""
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

    #  Create mock for datetime.datetine.now()
    expected = '2020-05-01 00:00:00'
    fake_now_dt = datetime.datetime.strptime(expected, '%Y-%m-%d %H:%M:%S')
    mock_datetime.datetime.now.return_value = fake_now_dt

    #  Creat message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12

    # Act
    dbhelpers.get_flavour(message, dbpath)

    # Assert
    #  Get new values
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT last_roll FROM players"""
    cursor.execute(query)
    output = cursor.fetchone()
    actual = output[0]
    cursor.close()
    conn.close()

    assert expected == actual

@patch('dbhelpers.dbhelpers.datetime')
def test_clear_inactive_records(mock_datetime, dbpath):
    # Arrange
    expected = [
        (10, 11, 13, 1, 'default', '2020-05-30 12:34:56'),
        (10, 11, 14, 1, 'default', '2020-05-01 12:34:56'),
    ]
    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    queries = [
        """INSERT INTO players (server, channel, player, last_roll)
                           VALUES (10, 11, 12, '2020-04-01 12:34:56');""",
        """INSERT INTO players (server, channel, player, last_roll)
                           VALUES (10, 11, 13, '2020-05-30 12:34:56');""",
        """INSERT INTO players (server, channel, player, last_roll)
                           VALUES (10, 11, 14, '2020-05-01 12:34:56');"""]
    for query in queries:
        cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

    #  Create mock for datetime.datetime.now()
    fake_now = '2020-05-31 00:00:00'
    fake_now_dt = datetime.datetime.strptime(fake_now, '%Y-%m-%d %H:%M:%S')
    mock_datetime.datetime.now.return_value = fake_now_dt

    #  Link mock_datetime.timedelta to proper timedelta function
    mock_datetime.timedelta = datetime.timedelta

    # Act
    dbhelpers.clear_inactive_records(dbpath)

    # Assert
    #  Get new values
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT * FROM players"""
    cursor.execute(query)
    actual = cursor.fetchall()
    cursor.close()
    conn.close()

    assert len(expected) == len(actual)
    assert expected == actual


def test_unset_flavour(dbpath):
    # Arrange
    expected = 0
    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO players (server, channel, player, flavour)
                           VALUES (10, 11, 12, 1);"""

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

    #  Create message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12
    setting = 'off'

    # Actual
    dbhelpers.set_flavour(message, setting, dbpath)
    actual = dbhelpers.get_flavour(message, dbpath)

    # Assert
    assert expected == actual[0]


def test_set_splat(dbpath):
    # Arrange
    expected = 'mage'
    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO players (server, channel, player, flavour)
                           VALUES (10, 11, 12, 1);"""

    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

    #  Create message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12
    setting = 'mage'

    # Actual
    dbhelpers.set_splat(message, setting, dbpath)
    actual = dbhelpers.get_flavour(message, dbpath)

    # Assert
    assert expected == actual[1]


def test_delete_player(dbpath):
    # Arrange
    expected = [
        (10, 11, 13, 1, 'default', None),
        (10, 11, 14, 1, 'default', None),
    ]

    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    queries = [
        """INSERT INTO players (server, channel, player)
                           VALUES (10, 11, 12);""",
        """INSERT INTO players (server, channel, player)
                           VALUES (10, 11, 13);""",
        """INSERT INTO players (server, channel, player)
                           VALUES (10, 11, 14);"""]
    for query in queries:
        cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

    #  Create message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12

    # Actual
    dbhelpers.delete_content(message, 'user', dbpath)

    # Assert
    #  Get new values
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT * FROM players"""
    cursor.execute(query)
    actual = cursor.fetchall()
    cursor.close()
    conn.close()

    assert len(expected) == len(actual)
    assert expected == actual


def test_delete_channel(dbpath):
    # Arrange
    expected = [
        (10, 11, 14, 1, 'default', None),
    ]

    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    queries = [
        """INSERT INTO players (server, channel, player)
                           VALUES (10, 12, 12);""",
        """INSERT INTO players (server, channel, player)
                           VALUES (10, 12, 13);""",
        """INSERT INTO players (server, channel, player)
                           VALUES (10, 11, 14);"""]
    for query in queries:
        cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

    #  Create message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 12
    message.author.id = 12

    # Actual
    dbhelpers.delete_content(message, 'channel', dbpath)

    # Assert
    #  Get new values
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT * FROM players"""
    cursor.execute(query)
    actual = cursor.fetchall()
    cursor.close()
    conn.close()

    assert len(expected) == len(actual)
    assert expected == actual


def test_delete_server(dbpath):
    # Arrange
    expected = [
        (10, 12, 12, 1, 'default', None),
    ]

    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    queries = [
        """INSERT INTO players (server, channel, player)
                           VALUES (10, 12, 12);""",
        """INSERT INTO players (server, channel, player)
                           VALUES (15, 12, 13);""",
        """INSERT INTO players (server, channel, player)
                           VALUES (15, 11, 14);"""]
    for query in queries:
        cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

    #  Create message mock
    message = MagicMock()
    message.guild.id = 15
    message.channel.id = 12
    message.author.id = 12

    # Actual
    dbhelpers.delete_content(message, 'server', dbpath)

    # Assert
    #  Get new values
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT * FROM players"""
    cursor.execute(query)
    actual = cursor.fetchall()
    cursor.close()
    conn.close()

    assert len(expected) == len(actual)
    assert expected == actual


def test_get_prefix(dbpath):
    # arrange
    expected = '!!roll'
    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO prefixes (server, channel, prefix)
                           VALUES (10, 12, '!!roll');"""
    cursor.execute(query)
    cursor.close()
    conn.commit()
    conn.close()

    #  Create message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 12

    # actual
    actual = dbhelpers.get_prefix(message, dbpath)

    # assert
    assert expected == actual


def test_get_prefix_default(dbpath):
    # arrange
    expected = '@mention'

    #  Create message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 12

    # actual
    actual = dbhelpers.get_prefix(message, dbpath)
    # assert
    assert expected == actual


def test_set_prefix(dbpath):
    # arrange
    expected = '!stuff'
    query = """INSERT INTO prefixes (server, channel)
                                   VALUES (10, 12);"""
    conn, cursor = dbhelpers.connect(dbpath)
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

    #  Create message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 12

    # actual
    dbhelpers.set_prefix(expected, message, dbpath)
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT prefix FROM prefixes;"""
    cursor.execute(query)
    actual = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    # assert
    assert expected == actual