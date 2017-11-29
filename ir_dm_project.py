# from indexer import Indexer
# from ir_model import IRModel
# from data.bart_migration import BartMigration
# from data.bart_migration import BartMigration
# from data.frans_migration import FransMigration
# from db_handler import DbHandler
import json

from indexer.indexer import Indexer
from topics.lda import LDA


def main():
    print("Use django to launch project using: \'python.exe manage.py runserver\'")
    # IRModel()

    # DbHandler().create_tables()
    # BartMigration().migrate_from_csv()
    # FransMigration().parse_from_csv()


if __name__ == "__main__":
    main()
