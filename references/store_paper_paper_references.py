# For analysis of the results, run the following query:
# (Replace table name if changed in this file)
#  select paper2_id, title, count(*) as c from reference_paper_paper left join papers on reference_paper_paper.paper2_id = papers.id group by paper2_id order by c desc;

import sqlite3 as sq3
from time import process_time

# Configuration options
input_database_location = "../data/database.sqlite" # The NIPS database
output_database_location = "../data/references.sqlite" # File will be created if it does not exist
table_name = "reference_paper_paper"

print("Starting program. Expected running time: 2-3 minutes.")
print("Writing changes to table '{}'".format(table_name))
t_start = process_time()
input_con = sq3.connect(input_database_location)
output_con = sq3.connect(output_database_location)

# Remove the table in the output database if it already exists
print("Preparing output database")
output_con.execute("DROP TABLE IF EXISTS {};".format(table_name))
output_con.execute("VACUUM;")
output_con.execute("CREATE TABLE {}(reference_id INTEGER, paper_id INTEGER, paper2_id INTEGER, PRIMARY KEY(reference_id ASC));".format(table_name))

# Store a mapping of all paper titles to paper id's
print("Storing mapping of paper title -> id in memory")
paper_mapping = {}
for paper_title, paper_id in input_con.execute("SELECT title, id FROM papers;").fetchall():
    paper_mapping[paper_title] = paper_id

# Determine the paper title references in each paper, and store an insert query in memory
max_paper_id = input_con.execute("SELECT MAX(id) FROM papers;").fetchone()[0]
print("Searching paper titles in papers, generating insert query")
insert_paper_references_qry = "INSERT INTO {} (paper_id, paper2_id) VALUES ".format(table_name)
sep = ""
for paper_id, paper_text in input_con.execute("SELECT id, paper_text FROM papers;").fetchall():
    for paper_title, paper2_id in paper_mapping.items():

        if paper_text is None:
            break
        # TODO: For now ignore the following papers
        #  - 5096 (Distributed k-Means and k-Median Clustering on General Topologies) and
        #  - 3116 (Stability of K-Means Clustering)
        # Their titles have incorrect values in the database, 'Distributed',
        # and 'Stability of', respectively.
        if paper2_id in [5096, 3116, paper_id]:
            break
        
        search_text = paper_text
        ref_pos = paper_text.rfind("References")

        if ref_pos != -1:
            search_text = paper_text[ref_pos:]

        if paper_title in search_text:
            insert_paper_references_qry += "{}({},{})".format(sep, paper_id, paper2_id)
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