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
 * Windows support

## Usage

TBD


### Mirroring Resources

In addition to apt packages, the Apache Hadoop charms require a few binary
resources, which are normally hosted on Launchpad. If access to Launchpad
is not available, the `jujuresources` library makes it easy to create a mirror
of these resources:

    sudo pip install jujuresources
    juju-resources fetch --all /path/to/resources.yaml -d /tmp/resources
    juju-resources serve -d /tmp/resources

This will fetch all of the resources needed by this charm and serve them via a
simple HTTP server. The output from `juju-resources serve` will give you a
URL that you can set as the `resources_mirror` config option for this charm.
Setting this option will cause all resources required by this charm to be
downloaded from the configured URL.

You can fetch the resources for all of the Apache Hadoop charms
(`apache-hadoop-hdfs-master`, `apache-hadoop-yarn-master`,
`apache-hadoop-compute-slave`, `apache-hadoop-plugin`, etc) into a single
directory and serve them all with a single `juju-resources serve` instance.


## Contact Information

- <bigdata@lists.ubuntu.com>


## Hadoop

- [InsightEdge](http://insightedge.io/) home page
