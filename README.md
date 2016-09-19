## Overview

InsightEdge is a high performance Spark distribution for low latency
workloads, high availability, and hybrid transactional/analytical
processing in one unified solution.

Features:

 * Exposes Data Grid as Spark RDDs
 * Saves Spark RDDs to Data Grid
 * Full DataFrames API support with persistence
 * Transparent integration with SparkContext using Scala implicits
 * Ability to select and filter data from Data Grid with arbitrary SQL and leverage Data Grid indexes
 * Running SQL queries in Spark over Data Grid
 * Data locality between Spark and Data Grid nodes
 * Storing MLlib models in Data Grid
 * Saving Spark Streaming computation results in Data Grid
 * Geospatial API, full geospatial queries support in DataFrames and RDDs
 * Off-Heap persistence
 * Interactive Web Notebook
 * Python support

## Usage

This charm requires Apache Spark and Apache Zeppelin.  It is recommended to
deploy this using the bundle:

    juju deploy cs:~gigaspaces/bundle/insightedge

You can then use `juju status` to get address for the service and then open
it in your web browser like `http://<address>:9090/`


## Contact Information

- <bigdata@lists.ubuntu.com>


## Additional Resources and Information

- [InsightEdge](http://insightedge.io/) home page
