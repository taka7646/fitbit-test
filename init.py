
import hashlib
import sqlite3
import argparse
from model import *
import db
import os

def main():
    parser = argparse.ArgumentParser()
    parser.parse_args()
    path = SQLITE3_NAME
    if not os.path.isfile(path):
        Base.metadata.create_all(db.engine)



if __name__ == "__main__":
    main()
