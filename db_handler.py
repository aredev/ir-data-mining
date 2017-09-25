import sqlite3


class DbHandler(object):
    def __init__(self, path="data/", filename="database.sqlite"):
        self.data_path = path
        self.db_name = filename
        self.conn = sqlite3.connect(self.data_path + self.db_name)
        self.cursor = self.conn.cursor

    def db_info(self):
        for name in self.get_table_names():
            print(name, "\t", len(self.conn.execute("SELECT * FROM " + name).fetchall()))

    def get_table_row_count(self, table):
        results = self.conn.execute("SELECT * FROM " + table).fetchall()
        return len(results)

    def get_table_rows_and_count(self, table):
        results = self.conn.execute("SELECT * FROM " + table).fetchall()
        return len(results), results

    def get_table_rows_author_paper_and_count(self):
        cursor = self.conn.execute("SELECT paper_authors.id, paper_id, author_id, name, year, title, event_type, pdf_name, abstract, paper_text FROM paper_authors LEFT JOIN authors ON paper_authors.author_id = authors.id LEFT JOIN papers ON paper_authors.paper_id = papers.id;" )
        results = cursor.fetchall()
        return len(results), results

    def get_table_names(self):
        results = self.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return [name[0] for name in results]

    def exec_query(self, query):
        results = self.conn.execute(query).fetchall()
        return results