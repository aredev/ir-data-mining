from indexer import Indexer
from lda import LDA


def main():
    # index = Indexer()
    LDA().build_lda_model()


if __name__ == "__main__":
    main()