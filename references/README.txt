The files in this directory are used to generate tables for the storage and
retrieval of references in the papers.

INPUT:
 * NIPS database. By default the scripts assume that it is located in
   '../data/dataabase.sqlite'.

OUTPUT:
 * ../data/references.sqlite: If it doesn't exist, it is created.

RUN SCRIPT:
 * Run 'py.exe ./store_paper_author_references.py' to create a relation of
   papers, and author id's of authors that are mentioned in it.
 * Run 'py.exe ./store_paper_paper_references.py' to create a relation of
   papers and paper id's of papers that are mentioned in it.


sample.py gives an example of how a list of paper ids, (or author ids) can be
obtained using Python.