from indexer import Indexer


def main():
    print("Use django to launch project using: \'python.exe manage.py runserver\'")

    indexer = Indexer()
    indexer.search("neural")


if __name__ == "__main__":
    main()
