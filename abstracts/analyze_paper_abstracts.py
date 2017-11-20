import matplotlib.pyplot as pp
import numpy as np
import sqlite3 as sq3

# This script is meant for visualizing the results of the store_paper_abstracts.py script.

database_location = "abstracts.sqlite"
table_name = "paper_abstracts"

con = sq3.connect(database_location)

abstract_lengths = []
for length, in con.execute("SELECT LENGTH(abstract) FROM {}".format(table_name)):
    abstract_lengths.append(length)

max_length = max(abstract_lengths)
bins = np.linspace(0, max_length, 100)
pp.hist(abstract_lengths, bins=bins)
pp.title('Histogram of abstract lengths (in characters)')
pp.show()
