from indexer.indexer import Indexer


def main():
    print("Use django to launch project using: \'python.exe manage.py runserver\'")

    indexer = Indexer()
    # indexer.get_index_information()
    indexer.search("susuki")


if __name__ == "__main__":
    main()
