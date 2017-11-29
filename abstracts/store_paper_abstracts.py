import regex as re
import sqlite3 as sq3
from time import process_time

# Approach:
# For each paper text, isolate the abstract section. Experimentally, the regex used has proven
# to lead to the best results, it extracts 3261 abstracts of the 3317 papers that don't have
# an abstract assigned.
#
# For a visualization of the results, change the parameters of the program, and view the results
# using the analyzer_paper_abstracts.py
#
# Not all abstracts are extracted (~56 are missing). The remaining texts are very hard to
# process, and methods to extract the abstracts automatically result in poorer abstracts for the
# remaining papers.

# Configuration options
input_database_location = "../data/database.sqlite" # The NIPS database
output_database_location = "abstracts.sqlite" # File will be created if it does not exist
table_name = "paper_abstracts" # The abstracts will be written to a separate table, to avoid overwriting the existing data

# Regexes for extracting the abstract section, and for removing the abstract subheader
abstract_rgx = re.compile(r'^[^a-z]*abstract.*?^([^a-z]*introduction|^1\s*)', re.IGNORECASE | re.DOTALL | re.MULTILINE)
abstract_sh_rgx = re.compile(r'[^a-z]*abstract[^a-z]*', re.IGNORECASE | re.DOTALL | re.MULTILINE)

print("Starting program. Expected running time: 0.5 seconds.")
print("Writing changes to table '{}'".format(table_name))
t_start = process_time()
input_con = sq3.connect(input_database_location)
output_con = sq3.connect(output_database_location)
paper_abstracts = {}

# Remove the table in the output database if it already exists
print("Preparing output database")
output_con.execute("DROP TABLE IF EXISTS {};".format(table_name))
output_con.execute("VACUUM;")
output_con.execute("CREATE TABLE {}(paper_id INTEGER, abstract TEXT);".format(table_name))

max_paper_id = input_con.execute("SELECT MAX(id) FROM papers;").fetchone()[0]
print("Extracting abstracts from paper texts")
for paper_id, paper_text in input_con.execute("SELECT id, paper_text FROM papers WHERE abstract='Abstract Missing';").fetchall():
    abspos = re.search(abstract_rgx, paper_text)
    if abspos is not None:
        abstract_text = paper_text[abspos.span()[0] : abspos.span()[1]]
        
        # Truncate the first and last line
        abstract_text = abstract_text[abstract_text.find('\n') + 1:]
        abstract_text = abstract_text[:abstract_text.rfind('\n') - 1]

        # Remove the abstract subheader strings
        abstract_text = re.sub(abstract_sh_rgx, '', abstract_text)

        # Cut at slightly above 2000 characters
        # (Nips website: "The abstract is submitted as plain text, with a maximum of 2000 characters")
        abstract_text = abstract_text[:min(len(abstract_text), 2500)]
        paper_abstracts[paper_id] = abstract_text

    print("{:6.2f}%".format(100 * paper_id / max_paper_id), end='\r')

# Insert the rows in the new table
print("Executing insert queries")
for paper_id, paper_abstract in paper_abstracts.items():
    q = "INSERT INTO {} (paper_id, abstract) VALUES (?, ?)".format(table_name)
    output_con.execute(q, (paper_id, paper_abstract))

    print("{:6.2f}%".format(100 * paper_id / max_paper_id), end='\r')
output_con.commit()

# Close the databases
input_con.close()
output_con.close()
print("Done. Time: {:10.2f}s".format(process_time() - t_start))