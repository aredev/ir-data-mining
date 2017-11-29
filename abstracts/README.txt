The files in this directory are used to extract the abstracts from the
papers.

INPUT:
 * NIPS database. By default the scripts assume that it is located in
   '../data/database.sqlite'.

OUTPUT:
 * abstracts.sqlite: If it doesn't exist, it is created. The data is writen to
   a separate database to avoid overwriting existing data.

RUN SCRIPT:
 * Run 'py.exe ./store_paper_abstracts.py' to extract the abstracts of all
   papers.
 * Run 'py.exe ./analyze_paper_abstracts.py' to display a histogram of the
   abstract lengths as indication of the correctness of the script.
