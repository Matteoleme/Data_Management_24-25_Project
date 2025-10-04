# Data Management Project
Data Management 2024/2025 
## Comparison between NoSQL tool and a relational DBMS
In this project, I aim to compare NoSQL and SQL systems to highlight the advantages and disadvantages of each technology. By carrying out this work, I expect to gain a clearer understanding of what they are, when to use them, and especially how to apply these two types of systems effectively.

### SQL vs NoSQL
For decades, SQL databases have been the standard for storing data. 
They organize information in a structured way, with a simple data model, efficient concurrency management, and a standardized query language. SQL databases are based on the relational model: data is stored in tables and connected through relations.

**Why was NoSQL introduced?**  
The rise of Big Data created new requirements that the relational model was not designed to handle. Queries over very large datasets became costly, and above all, rigid schemas could not easily support variety and flexibility.

**Main characteristics of NoSQL systems:**
-   Schemaless design
-   Do not rely only on SQL
-   Often built to run on clusters
-   Do not always guarantee strong consistency with ACID transactions

**Types of NoSQL data models based on aggregates:**

-   Key-Value Stores
-   Column-Family Stores
-   Document-based Databases

**Document-based databases** store data as _documents_, which are sets of key-value pairs. Values can also be complex structures, allowing for nesting. A document can be seen as an object in Object-Oriented Programming. This model offers more flexibility than key-value or column-family stores. Documents are typically stored in JSON format.

### Used technologies
**Tools:** **PostgreSQL** (v17.5) and **MongoDB** (v8.0.13).
Both systems are run in separate Docker containers on my local hardware. This approach makes it easier to manage the tools, ensures isolated environments, and avoids problems with versioning or conflicts with other software on my PC.

**For interaction and exploration**, I use **DBeaver** for PostgreSQL and **MongoDB Compass**. These tools help me visualize the dataset more clearly and quickly test some queries.

**For the actual analysis**, I use Python with the respective libraries: `psycopg2` for PostgreSQL and `pymongo` for MongoDB. This allows me to automate the process and obtain cleaner results.

### Dataset
First, I chose a dataset about football transfers. However, after running some queries, I realized that it contained too few rows (despite having many tables and attributes) to perform a meaningful analysis. Most of the queries finished in less than one second.

Then I switched to a different dataset: in this case, there are only three tables with a smaller number of attributes, but a much larger amount of data: more than five million rows in the _flights_ table.

**Dataset description**
- **Link**: https://www.kaggle.com/datasets/usdot/flight-delays/
-   **Context**: The U.S. Department of Transportation's (DOT) Bureau of Transportation Statistics tracks the on-time performance of domestic flights operated by large air carriers. Summary information on the number of on-time, delayed, canceled, and diverted flights is published in DOT's monthly _Air Travel Consumer Report_ and in this dataset of 2015 flight delays and cancellations.
-   **Size**: 592.43 MB
-   **Structure**:
    -   _Flights_: 31 columns, more than 5 million rows
    -   _Airlines_: 2 columns, 14 rows
    -   _Airports_: 322 columns, 7 rows

### Import Procedure
To import the dataset from CSV into both SQL and NoSQL systems, I used the standard automatic procedures provided by the tools (PostgreSQL and MongoDB Compass). I selected the same files for both systems, and the tools handled the import automatically.

For the denormalized dataset, instead, I wrote a simple Python script to transform normalized CSV files into a new structure optimized for NoSQL storage.
Since the denormalized dataset was very large (due to redundancy), I could not use MongoDB Compass directly. I therefore used the CLI command to import the dataset:

    mongoimport \
    --uri "mongodb://user:password@localhost:27017/airlinesDB?authSource=admin" \
        --collection flights_denormalized \
        --file /path/flights_denorm.json

### Methodology
To perform the analysis, I write two small Python scripts that automatically send queries to both the SQL and NoSQL systems.

The main idea is to run two types of tests:
1.  Use the built-in **_EXPLAIN_** command of each tool. This allows me to measure the actual server-side execution time.
    
2.  Run the query and put the result in a data structure to simulate a **real interaction between the user and the data**.

Each test is repeated multiple times to obtain a more accurate approximation of execution times.

#### Explain Command
##### MongoDB
The explain command allows you to get information on query execution. This command supports three different verbosity levels:
1. *queryPlanner*: provides the selected query plan
2. *executionStats*: *queryPlanner* plus statistics like execution time and number of returned documents
3. *allPlansExecution*: *executionStats* and also all information about rejected query plans

In my project I used the *executionStats* verbosity, in particular the field: 

    explain.executionStats.executionTimeMillis

that reports the total time in ms required for query plan selection and query execution.

In the case of update or delete operations, the explain command doesn't apply modification to the data 

> [Medium](https://medium.com/techieahead/everything-you-need-to-know-about-mongodb-explain-265cb1a42927)
> [MongoDB Docs](https://www.mongodb.com/docs/manual/reference/method/db.collection.explain/#mongodb-method-db.collection.explain)

##### PostgreSQL
This command displays the execution plan generated by the planner, that includes also the estimated execution cost. In my project I added also the *ANALYZE* option to actually execute the query, which allowed me to see the real elapsed time.

> [postgresql.org](https://www.postgresql.org/docs/current/sql-explain.html)

#### Environment
All experiments are run on my laptop connected to the electric power:
-   CPU: Intel i5 (13th generation)
-   RAM: 16 GB
-   Storage: NVMe SSD

### Tested Queries

I tested different queries covering various scenarios. Whenever possible, I applied a `LIMIT` to see how execution time changes with different result sizes.

-   **Simple SELECT**: return all values from the _flights_ table
	- SQL: `SELECT * FROM flights`
	- NoSQL: `db.flights.find({})`
    - Limits tested: 100000 · 1000000 · 5000000 rows
        
-   **Simple filter**: filter on the attribute `ORIGIN_AIRPORT`
    - SQL: `select * from flights f where f."ORIGIN_AIRPORT" = 'LAX'`
    - NoSQL: `db.flights.find({ ORIGIN_AIRPORT" = 'LAX' })`
    -   Limits tested: 100000 · 1000000 rows
        
-   **Complete JOIN**: join the three tables into a single result
    - SQL: 
    - Normalized NoSQL: 
    - Denormalized NoSQL:
    -   Limits tested: 100000 · 1000000 rows
        
-   **GROUP BY**: group the _flights_ table on the `AIRLINE` attribute
    
-   **GROUP BY with JOIN**: same as before, but joining also with _airlines_ to print the airline name


### Actual procedure

First, I tested the simple _SELECT_ and simple _FILTER_ queries on both systems. After that, I moved to the complete _JOIN_: as expected, the NoSQL query was much slower.

The last two queries involved _GROUP BY_. Here I noticed that the first execution was significantly slower than the following ones on both systems. After some analysis, I realized this difference was caused by cached data.

For this reason, I decided to run two types of analyses:

1.  **No cache execution** – to achieve this, I manually restarted the container before each run.
    
2.  **Cached execution** – in this case, I performed two “warm-up” runs first, and then measured the timing of the following execution.

### Optimizations

The true strength of a NoSQL system lies in the **denormalized organization** of the dataset. After the first round of tests, I decided to re-run the analysis in a smarter way:

1.  I reorganized the NoSQL dataset into a single collection, in order to improve performance on the complete _JOIN_ query.
    
2.  In the _flights_ collection, I also included the airline information and kept a separate _airports_ collection. This allowed to improve performance on the _GROUP BY with JOIN_ query, since no join was needed anymore.

As mentioned before, the denormalized versions of the dataset were very large due to redundancy — over **7 GB**.  
For this reason, I had to rename some fields to reduce the file size and speed up the import process, while still keeping all the relevant information. This way I could ensure a fair comparison between the SQL and NoSQL systems without missing any attribute.

