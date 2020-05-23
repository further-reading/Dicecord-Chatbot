from dicecord import runner, saver
from utils.tokens import test_token
from dbhelpers import *
import sys

if __name__ == '__main__':
    dbpath = sys.argv[1]
    try:
        dbhelpers.create_tables(dbpath)
    except dbhelpers.db.OperationalError:
        # table already exists
        pass
    runner(test_token, saver, dbpath)
