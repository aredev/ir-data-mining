import sqlite3


class DbHandler(object):
    __instance = None

    @staticmethod
    def get_instance():
        if DbHandler.__instance is None:
            DbHandler()
        return DbHandler.__instance

    def __init__(self, path="data/", filename="database.sqlite"):
        self.data_path = path
        self.db_name = filename
        self.conn = sqlite3.connect(self.data_path + self.db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        create_papers_table = """
         CREATE TABLE IF NOT EXISTS papers (
            id integer PRIMARY KEY,
            doc_id integer NOT NULL,
            title text NOT NULL,
            year text NOT NULL,
            abstract text
         );
        """
        self.cursor.execute(create_papers_table)
        #
        # drop_authors_table = """
        # DROP TABLE authors;
        # """
        # self.cursor.execute(drop_authors_table)

        create_authors_table = """
                 CREATE TABLE IF NOT EXISTS authors (
                    id integer PRIMARY KEY,
                    name text NOT NULL,
                    score integer NOT NULL
                 );
                """
        self.cursor.execute(create_authors_table)

        create_references_table = """ 
        CREATE TABLE IF NOT EXISTS `references` (
            `id`	INTEGER PRIMARY KEY AUTOINCREMENT,
            `paper_id`	INTEGER NOT NULL,
            `reference_paper_id`	INTEGER NOT NULL,
            
            CONSTRAINT paper_reference_unique UNIQUE(paper_id, reference_paper_id)
        );
        """
        self.cursor.execute(create_references_table)

        create_topics_table = """ 
        CREATE TABLE IF NOT EXISTS `topics` (
            `id` integer PRIMARY KEY,
            `name` text NOT NULL
        );
        """
        self.cursor.execute(create_topics_table)

        create_topic_papers_table = """
        CREATE TABLE IF NOT EXISTS `paper_topics` (
            `id` integer PRIMARY KEY,
            `paper_id` integer NOT NULL,
            `topic_id` integer NOT NULL,
            `probability` FLOAT NOT NULL,
            
            CONSTRAINT paper_topic_unique UNIQUE(paper_id, topic_id)
        );
        """
        self.cursor.execute(create_topic_papers_table)

        create_suggested_authors_table = """
        CREATE TABLE IF NOT EXISTS `suggested_authors` (
            `id` integer PRIMARY KEY,
            `author_id` integer NOT NULL,
            `suggested_author_id` integer NOT NULL,

            CONSTRAINT author_suggested_author_unique UNIQUE (author_id, suggested_author_id)
        );
        """
        self.cursor.execute(create_suggested_authors_table)

        create_topic_evolutions_table = """
        CREATE TABLE IF NOT EXISTS `topic_evolutions` (
            `id` integer PRIMARY KEY,
            `topic_id` integer NOT NULL,
            `year` text NOT NULL,
            `score` integer NOT NULL,

            CONSTRAINT topic_year_unique UNIQUE (year, topic_id)
        );
        """
        self.cursor.execute(create_topic_evolutions_table)

        create_paper_suggested_authors = """
        CREATE TABLE IF NOT EXISTS `paper_suggested_authors` (
            `id` INTEGER PRIMARY KEY,
            `author_id` INTEGER NOT NULL,
            `paper_id` INTEGER NOT NULL,
            `similarity` FLOAT,

            CONSTRAINT author_paper_unique UNIQUE (author_id, paper_id)
        );
        """
        self.cursor.execute(create_paper_suggested_authors)

        create_suggested_papers_table = """
             CREATE TABLE IF NOT EXISTS `suggested_papers` (
                 `id` INTEGER PRIMARY KEY,
                 `paper_id` INTEGER NOT NULL,
                 `suggested_paper_id` INTEGER NOT NULL,

                 CONSTRAINT paper_suggested_paper UNIQUE (paper_id, suggested_paper_id)
             );
             """
        self.cursor.execute(create_suggested_papers_table)
        #
        alter_author_table = """
            DROP TABLE IF EXISTS `authors`;
        """
        self.cursor.execute(alter_author_table)

        add_new_author_table = """
        CREATE TABLE `authors` (
                    `id` INTEGER PRIMARY KEY,
                    `name` TEXT NOT NULL,
                    `pagerank` FLOAT,
                    `h_index` INTEGER
                );
        """

        self.cursor.execute(add_new_author_table)


        # add_column_to_suggested = """
        # ALTER TABLE `suggested_authors` ADD COLUMN `score` FLOAT;
        # """
        #
        # self.cursor.execute(add_column_to_suggested)

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
        query = "SELECT author_id from paper_authors WHERE paper_id == " + str(paper_id)
        authors = self.conn.execute(query).fetchall()
        return [str(author[0]) for author in authors]

    def get_author_by_id(self, author_id):
        query = "SELECT name FROM authors WHERE id == " + str(author_id)
        return self.conn.execute(query).fetchone()[0]