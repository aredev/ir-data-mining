
from indexer import Indexer
from ir_model import IRModel


def main():
    print("Use django to launch project using: \'python.exe manage.py runserver\'")

    indexer = Indexer()
    # indexer.get_index_information()
    indexer.search("susuki")
    # indexer = Indexer()
    # indexer.search("neural")

    IRModel()


if __name__ == "__main__":
    main()
