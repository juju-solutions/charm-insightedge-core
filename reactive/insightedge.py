# pylint: disable=unused-argument
import os
import subprocess
from charms.reactive import when, when_not, is_state, set_state, remove_state
from charmhelpers.core.hookenv import status_set, resource_get, log
from charmhelpers.core.host import chdir
from charmhelpers.core import unitdata, host
from distutils import dir_util
from jujubigdata import utils


@when_not('insightedge.fetched')
def fetch_insightedge():
    status_set("maintenance", "fetching insightedge")
    result = resource_get('InsightEdgeDiff')
    if not result:
        status_set("blocked", "unable to fetch insightedge resource")
        log("Failed to fetch InsightEdge resource")
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
    status_set('maintenance', 'installing insightedge')
    files = dir_util.copy_tree('/var/tmp/InsightEdge-1.0.0-juju-diff',
                               '/usr/lib/spark/')
    log("Files copied over from InsightEdge")
    for f in files:
        log(f)

    set_state('insightedge.on.spark')
    update_status()


@when('insightedge.on.spark')
@when_not('spark.ready')
def remove_insightedge_from_spark(spark):
    remove_state('insightedge.on.spark')
    remove_state('insightedge.ready')
    update_status()


@when_not('insightedge.on.zeppelin')
@when('insightedge.fetched')
@when('zeppelin.joined')
def setup_insightedge_on_zeppelin(zeppelin):
    status_set('maintenance', 'registering notebook with zeppelin')
    nb_path = '/var/tmp/InsightEdge-1.0.0-juju-diff/zeppelin/notebook'
    for note_dir in os.listdir(nb_path):
        if note_dir.startswith('INSIGHTEDGE-'):
            zeppelin.register_notebook(os.path.join(nb_path,
                                                    note_dir,
                                                    'note.json'))
    zeppelin.modify_interpreter(
        interpreter_name='spark',
        properties={
            'insightedge.locator': '127.0.0.1:4174',
            'insightedge.group': 'insightedge',
            'insightedge.spaceName': 'insightedge-space',
            'spark.externalBlockStore.blockManager': 'org.apache.spark.storage.InsightEdgeBlockManager',
        },
    )
    set_state('insightedge.on.zeppelin')
    update_status()


@when('zeppelin.notebook.rejected')
def rejected_notebook(zeppelin):
    raise ValueError('Notebook rejected: {}'.format(
        ', '.join(zeppelin.rejected_notebooks())))


@when('insightedge.on.zeppelin')
@when_not('zeppelin.joined')
def remove_insightedge_from_zeppelin():
    remove_state('insightedge.on.zeppelin')
    remove_state('insightedge.ready')
    update_status()


@when_not('insightedge.ready')
@when('insightedge.on.spark', 'insightedge.on.zeppelin')
def restart_services():
    stop_services()
    start_services()
    set_state('insightedge.ready')
    update_status()


def start_services():
    host.service_start('spark-master')
    host.service_start('spark-slave')
    # TODO: all these configs
    subprocess.call(["/usr/lib/spark/sbin/start-datagrid-master.sh",
                     "-m", "localhost",
                     "-s", "1G"])
    subprocess.call(["/usr/lib/spark/sbin/start-datagrid-slave.sh",
                     "--master", "localhost",
                     "--locator", "localhost:4174",
                     "--group", "insightedge",
                     "--name", "insightedge-space",
                     "--topology", "2,0",
                     "--size", "1G",
                     "--instances", "id=1;id=2"])


def stop_services():
    if utils.jps("HistoryServer"):
        host.service_stop('spark-history')
    if utils.jps("Master"):
        host.service_stop('spark-master')
    if utils.jps("Worker"):
        host.service_stop('spark-slave')
    if utils.jps("insightedge.marker=master"):
        d = dict(os.environ)
        d["TIMEOUT"] = str(10)
        cmd = "/usr/lib/spark/sbin/stop-datagrid-master.sh"
        subprocess.call(cmd, shell=True, env=d)
    if utils.jps("insightedge.marker=slave"):
        cmd = "/usr/lib/spark/sbin/stop-datagrid-slave.sh"
        subprocess.call(cmd, shell=False)


def update_status():
    spark_rel = is_state('spark.ready')
    zeppelin_rel = is_state('zeppelin.joined')
    iedge_ready = is_state('insightedge.ready')

    if not spark_rel and not zeppelin_rel:
        status_set('blocked',
                   'Waiting for relation to Spark and Zeppelin')
    elif spark_rel and not zeppelin_rel:
        status_set('blocked', 'Waiting for relation to Zeppelin')
    elif spark_rel and not zeppelin_rel:
        status_set('blocked', 'Waiting for relation to Spark')
    elif not iedge_ready:
        status_set('waiting', 'Waiting for services to restart')
    else:
        status_set('active', 'Ready')
