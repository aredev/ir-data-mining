# For analysis of the results, run the following query:
# (Replace table name if changed in this file)
#  select author_id, name, count(*) as c from reference_paper_author left join authors on authors.id = reference_paper_author.author_id group by author_id order by c desc;

import sqlite3 as sq3
from time import process_time

# Configuration options
input_database_location = "../data/database.sqlite" # The NIPS database
output_database_location = "../data/references.sqlite" # File will be created if it does not exist
table_name = "reference_paper_author"

print("Starting program. Expected running time: 5-6 minutes.")
print("Writing changes to table '{}'".format(table_name))
t_start = process_time()
input_con = sq3.connect(input_database_location)
output_con = sq3.connect(output_database_location)

# Remove the table in the output database if it already exists
print("Preparing output database")
output_con.execute("DROP TABLE IF EXISTS {};".format(table_name))
output_con.execute("VACUUM;")
output_con.execute("CREATE TABLE {}(reference_id INTEGER, paper_id INTEGER, author_id INTEGER, PRIMARY KEY(reference_id ASC));".format(table_name))

# Store a mapping of all author names to author id's
print("Storing mapping of author name -> id in memory")
author_mapping = {}
for author_name, in input_con.execute("SELECT DISTINCT(name) FROM authors;").fetchall():
    author_mapping[author_name] = input_con.execute("SELECT MIN(id) FROM authors WHERE name = \"" + author_name + "\";").fetchone()[0]

# Approach:
# For each paper text:
#  1. Search for the latest occurence of the string 'References' (this exists
#     in 96.62% of all papers). If it exists, search for references in the text
#     after it, otherwise search in the full text.
#  2. Loop over the author names, and search for the literal occurence in the
#     text. If the author name string occurs, update the query such that a row
#     is appended with the document id and author id of the match.
#
# Converting to lowercase, using regex search or concatenating lines of the paper
# text does not improve results. Especially searching for matching authors using
# a sql query is *very* slow. Using a naive search for author names returns the
# best results.

# Determine the author references in each paper, and store an insert query in memory
max_paper_id = input_con.execute("SELECT MAX(id) FROM papers;").fetchone()[0]
print("Searching author names in papers, generating insert query")
insert_paper_references_qry = "INSERT INTO {} (paper_id, author_id) VALUES ".format(table_name)
sep = ""
for paper_id, paper_text in input_con.execute("SELECT id, paper_text FROM papers;").fetchall():
    for author_name, author_id in author_mapping.items():
        search_text = paper_text
        ref_pos = paper_text.rfind("References")

        if ref_pos != -1:
            search_text = paper_text[ref_pos:]

        if author_name in search_text:
            insert_paper_references_qry += "{}({},{})".format(sep, paper_id, author_id)
            sep = ","
    print("{:6.2f}%".format(100 * paper_id / max_paper_id), end='\r')

# Insert the rows in the new table
print("Executing insert query")
output_con.execute(insert_paper_references_qry)
output_con.commit()

# Close the databases
input_con.close()
output_con.close()
print("Done. Time: {:10.2f}s".format(process_time() - t_start))