# Wikipedia-Search-Engine
In this project I have implemented a search engine over the 40 GB Wikipedia dump. Both simple and multi field queries have been implemented. The search returns a ranked list of articles in real time.

# Step 1 : Installing Requirements
Since I use an external stemmer, you must install "stemming" module for python using pip (Mentioned in requirements.txt)

# Step 2 : Parsing the Data
To parse the data, run the file "index.py" To run the file, the syntax is "python3 index.py <path_to_wiki_dump> <path_to_invertedindex_output> <invertedindex_stat.txt>". It'll parse the whole dump and file the index files in the 'indexFiles' directory. It also creates the document to title mapping file in the current directory named 'docTitleMap.txt' which will be used by the search module later. (NOTE : As of current code, it pushes the index to disk for every 4000 documents encountered. This can be changed by changing the value of 'pushLimit' variable in the code)

# Step 3 : Merging the Indexes and Creating Secondary Indexes
There isn't any need for command line arguments. It takes the index files from 'indexFiles' directory and populates the 'finalIndex' directory with indexes of given chunk size and creates a secondary index named 'secondaryIndex.txt' in the same folder. (NOTE : As of the current code, the chunk size is kept 150000. This can be changed by changing the value of 'chunkSize' variable in the code)

# Step 4 : Running the Search Engine
To search for queries, run the file 'search.py'. It loads the index from 'finalIndex' (both primary and secondary). It also uses the file 'docTitleMap.txt' (which must be in the working directory) to display titles corresponding to the docIDs. After it loads up, it gives the user a prompt to enter the query. After that the result of query is displayed. (top K results). The format of result is: : (Here the ID is from the XML Dump) ...

To specify normal queries, type them normally. For Field Queries, follow the format: f1: f2: ... where f1,f2 are fields : t - title, b - body, r - references, i - infobox, c - categories, e - external links
