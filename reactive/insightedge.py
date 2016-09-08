# pylint: disable=unused-argument
import subprocess
from charms.reactive import when, when_not, when_none, is_state, set_state, remove_state
from charmhelpers.core.hookenv import status_set, resource_get, log
from charmhelpers.core.host import chdir
from charmhelpers.core import unitdata
from distutils import dir_util


@when_not('insightedge.fetched')
def setup_insightedge_on_spark():
    result = resource_get('InsightEdgeDiff')
    if not result:
        state_set("blocked", "Failed to fetch InsightEdge resource")
        log.("Failed to fetch InsightEdge resource")
        return

    unitdata.kv().set("insigthedgetarball", result)
    log("InsightEdgeDiff path is {}".format(result))
    with chdir('/var/tmp'):
        cmd = 'tar -zxvf {}'.format(result).split()
        subprocess.call(cmd, shell=False)

    set_state('insightedge.fetched')


@when_not('insightedge.on.spark')
@when('insightedge.fetched')
@when('spark.ready')
def setup_insightedge_on_spark(spark):
    status_set('waiting', 'Deploying InsightEdge')
    files = dir_util.copy_tree('/var/tmp/InsightEdge-1.0.0-juju-diff', '/usr/lib/spark/')
    log("Files copied over from InsightEdge")
    for f in files:
        log(f)

    update_status()
    set_state('insightedge.on.spark')


@when('insightedge.on.spark')
@when_not('spark.ready')
def remove_insightedge_from_spark(spark):
    update_status()
    remove_state('insightedge.on.spark')


@when_not('insightedge.on.zeppelin')
@when('insightedge.fetched')
@when('zeppelin.ready')
def setup_insightedge_on_spark(zeppelin):
    update_status()
    set_state('insightedge.on.zeppelin')


@when('insightedge.on.zeppelin')
@when_not('zeppelin.ready')
def remove_insightedge_from_zeppelin(spark):
    update_status()
    remove_state('insightedge.on.zeppelin')


def update_status():
    spark_rel = is_state('spark.ready')
    zeppelin_rel = is_state('zeppelin.ready')

    if not spark_rel and not zeppelin_rel:
        status_set('blocked',
                   'Waiting for relation to Spark and Zeppelin')
    elif spark_rel and not zeppelin_rel:
        status_set('blocked', 'Waiting for relation to Zeppelin')
    elif spark_rel and not zeppelin_rel:
        status_set('blocked', 'Waiting for relation to Spark')
    else:
        status_set('active', 'Ready')
