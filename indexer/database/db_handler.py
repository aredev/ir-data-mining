import os
import sqlite3


class DbHandler(object):
    __instance = None

    @staticmethod
    def get_instance():
        if DbHandler.__instance is None:
            DbHandler()
        return DbHandler.__instance

    def __init__(self, path="../ir-data-mining/data/", filename="database.sqlite"):
        if not os.path.exists(path + filename):
            raise FileNotFoundError("Could not find the database file at the following location:\n{}".format(
                os.path.abspath(path + filename)))
        self.data_path = path
        self.db_name = filename
        self.conn = sqlite3.connect(self.data_path + self.db_name)
        self.cursor = self.conn.cursor()
        self.doc_ids = self._get_doc_ids()
        # self.create_tables()

    def create_tables(self):
        create_papers_table = """
         CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY,
            doc_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            year TEXT NOT NULL,
            abstract TEXT
         );
        """
        self.cursor.execute(create_papers_table)

        drop_authors_table = """ 
        DROP TABLE authors;
        """
        self.cursor.execute(drop_authors_table)

        create_authors_table = """
                 CREATE TABLE IF NOT EXISTS authors (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    score INTEGER NOT NULL
                 );
                """
        self.cursor.execute(create_authors_table)

        create_references_table = """ 
        CREATE TABLE IF NOT EXISTS `references` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `paper_id` INTEGER NOT NULL,
            `reference_paper_id` INTEGER NOT NULL,

            CONSTRAINT paper_reference_unique UNIQUE(`paper_id`, `reference_paper_id`)
        );
        """
        self.cursor.execute(create_references_table)

        create_topics_table = """ 
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
        self.cursor.execute(create_topics_table)

        create_topic_papers_table = """
        CREATE TABLE IF NOT EXISTS paper_topics (
            id INTEGER PRIMARY KEY,
            paper_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,

            CONSTRAINT paper_topic_unique UNIQUE(paper_id, topic_id)
        );
        """
        self.cursor.execute(create_topic_papers_table)

        create_suggested_authors_table = """
        CREATE TABLE IF NOT EXISTS suggested_authors (
            id INTEGER PRIMARY KEY,
            author_id INTEGER NOT NULL,
            suggested_author_id INTEGER NOT NULL,

            CONSTRAINT author_suggested_author_unique UNIQUE (author_id, suggested_author_id)
        );
        """
        self.cursor.execute(create_suggested_authors_table)

        create_topic_evolutions_table = """
        CREATE TABLE IF NOT EXISTS topic_evolutions (
            id INTEGER PRIMARY KEY,
            topic_id INTEGER NOT NULL,
            year TEXT NOT NULL,
            score INTEGER NOT NULL,

            CONSTRAINT topic_year_unique UNIQUE (year, topic_id)
        );
        """
        self.cursor.execute(create_topic_evolutions_table)

        create_paper_suggested_authors = """
        CREATE TABLE IF NOT EXISTS paper_suggested_authors (
            id INTEGER PRIMARY KEY,
            author_id INTEGER NOT NULL,
            paper_id INTEGER NOT NULL,

            CONSTRAINT author_paper_unique UNIQUE (author_id, paper_id)
        );
        """
        self.cursor.execute(create_paper_suggested_authors)

        print("Alter author table?")
        alter_author_table = """ 
        DROP TABLE authors;
        CREATE TABLE authors (
            id INTEGER PRIMARY KEY;
            name TEXT NOT NULL;
            pagerank FLOAT NOT NULL;
            h_index INTEGER NOT NULL;
        );
        """

        self.cursor.execute(alter_author_table)

        add_column_to_suggested = """
        ALTER TABLE `suggested_authors` ADD COLUMN `similarity` FLOAT;
        """

        self.cursor.execute(add_column_to_suggested)



    def db_info(self):
        for name in self.get_table_names():
            print(name, "\t", len(self.conn.execute("SELECT * FROM " + name).fetchall()))

    def get_table_row_count(self, table):
        results = self.conn.execute("SELECT * FROM " + table).fetchall()
        return len(results)

    def get_table_rows_and_count(self, table):
        results = self.conn.execute("SELECT * FROM " + table).fetchall()
        return len(results), results

    def get_table_names(self):
        results = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return [name[0] for name in results]

    def exec_query(self, query):
        results = self.conn.execute(query).fetchall()
        return results

    def get_authors_by_paper_id(self, paper_id):
        query = "SELECT author_id FROM paper_authors WHERE paper_id == " + str(paper_id)
        authors = self.conn.execute(query).fetchall()
        return [str(author[0]) for author in authors]

    def get_title_by_paper_id(self, paper_id):
        query = "SELECT title FROM papers WHERE id == " + paper_id
        title = self.conn.execute(query).fetchone()
        return title

    def get_author_by_id(self, author_id):
        query = "SELECT name FROM authors WHERE id == " + str(author_id)
        return self.conn.execute(query).fetchone()[0]

    def insert_paper_and_its_authors(self, paper, authors):
        """
        Insert a paper, list of authors and the link between them
        :param paper:
        :param authors:
        :return:
        """
        insert_paper_query = "INSERT INTO papers(id, title, year, pdf_name, abstract, paper_text) VALUES (" + \
                             str(paper.docId) + "," + str(paper.title) + "," + str(paper.year) + "," + str(
            paper.pdfName) + "," + \
                             str(paper.abstract) + str(paper.text) + ");"
        self.conn.execute(insert_paper_query)
        paper_id = self.cursor.lastrowid

        for author in authors:
            insert_author_query = "INSERT INTO authors(name, score) VALUES ( " + str(author.name) + ", " + str(
                author.score) + " );"
            self.conn.execute(insert_author_query)
            author_id = self.cursor.lastrowid

            insert_author_paper_query = "INSERT INTO paper_authors(paper_id, author_id) VALUES ( " + str(paper_id) + \
                                        "," + str(author_id) + ");"
            self.conn.execute(insert_author_paper_query)

    def _get_doc_ids(self):
        """
        Get all of the doc ids in the collection of publications.
        :return: list of all the doc ids for all of the publications
        """
        doc_ids = []
        count, corpus = self.get_table_rows_and_count("papers")
        for doc in corpus:
            doc_ids.append(doc[0])
        return doc_ids

    def get_index_for_docid(self, docId):
        """
        Determine the index of the publication in the list of all publications given the doc id.
        The reason for this function is that given doc ids are not successive: there are gaps of more than 1 between
        successive doc ids.
        :param docId: The doc id
        :return: The index of the doc id in the list of publications. In it was not present, -1 will be returned.
        """
        try:
            return self.doc_ids.index(int(docId))
        except Exception as e:
            return -1
