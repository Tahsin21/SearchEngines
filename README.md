# SearchEngines
Overview:

Collection of programs that parse through a Gzip file to create an IndexEngine, Lexicon Engine and MetaData Engine. It is then able to find documents that are similar to query input using BM25, and BooleanAND with the addition of query-based snippets per entry.

These programs were written in Python3. To run, make sure to have Python3 installed. Then in terminal, cd into the folder in which the .py files are located and run: python3 __.py

IndexEngine.py takes a GZIP File and can parse through the entire file and organize each document contained within the <DOC> </DOC> tags. It creates a file hierarchy based on the document's date and stores all the documents in their respective file. It will also create .txt files that compile all the documents'metadata, lexicon engine, and inverted index.

Ensure an Index file is created from IndexEngine.py before executing the SearchEngine.py program.


