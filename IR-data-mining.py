from Indexer import Indexer


def main():
    path = "data/"
    filename = "database.sqlite"
    index = Indexer(path, filename)
    index.db_info()
    index.tokenize()


if __name__ == "__main__":
    main()
