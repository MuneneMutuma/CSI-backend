# Court Smart Insights - Backend
This is a part of my final year project. It contains the code for the backend.

## Folder Structure

The structure of the folder is as follows:

```bash
.
├── csi_api
│   ├── api
│   ├── csi_api
│   ├── db.sqlite3
│   └── manage.py
├── data
│   ├── crawler
│   └── files
├── graph
│   ├── duplicates.csv
│   └── feed.ipynb
├── rdf.owx
├── README.md
├── requirements.txt
└── search
    └── solr
```

### 1. csi_api
csi_api contains a `DjangoRestFramework` API, that exposes the endpoint(s) to interactwith the system

### 2. data
Contains the crawler for scraping case law files. The actual case law files have not been uploaded due to size constraints.

### 3. graph
Sub project folder for feeding data to the graph.

### 4. search
Sub project folder for indexing documents for search

### files
1. requirements.txt - contains the python modules used for this project
2. rdf.owx - RDF specification file for graph

## API 
1. `POST /api/v1/query`
send a post request to get results of query.
```python
payload = {
    'query': '<query>' 
}
```

## Tools
1. Solr
2. Python
3. Neo4j