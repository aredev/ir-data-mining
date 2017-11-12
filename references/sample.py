# Get paper or author references given a paper id:

import sqlite3

import sqlite3
database_location = "../data/references.sqlite"

con = sqlite3.connect(database_location)

# Get the referenced author id's in a list
print("Referenced authors")
paper_id = 6603
rows = con.execute("select author_id from reference_paper_author where paper_id = {}".format(paper_id)).fetchall()
result = [row[0] for row in rows]

print(result)

# Get the referenced paper id's in a list
# The referenced papers are quite sparse.
print()
print("Referenced papers")
paper_id = 4613
rows = con.execute("select paper2_id from reference_paper_paper where paper_id = {}".format(paper_id)).fetchall()
result = [row[0] for row in rows]

print(result)


con.close()