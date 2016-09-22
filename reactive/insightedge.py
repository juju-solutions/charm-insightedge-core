# pylint: disable=unused-argument
import os
import subprocess
from path import Path
from charms.reactive import when, when_not, set_state
from charms.reactive.helpers import data_changed
from charmhelpers.core import hookenv
from charmhelpers.core import host
from charmhelpers import fetch
from jujubigdata import utils


@when_not('spark.ready')
def report_waiting():
    hookenv.status_set('waiting', 'waiting for spark')


@when('spark.ready')
@when_not('insightedge.installed')
def setup_insightedge_on_spark(spark):
    destination = Path('/usr/lib/insightedge')
    if not destination.exists():
        hookenv.status_set('maintenance', 'fetching insightedge')
        filename = hookenv.resource_get('insightedge')
        if not filename:
            hookenv.status_set("blocked",
                               "unable to fetch insightedge resource")
            hookenv.log("Failed to fetch InsightEdge resource")
            return

        hookenv.status_set('maintenance', 'installing insightedge')
        extracted = Path(fetch.install_remote('file://' + filename))
        destination.rmtree_p()  # in case doing a re-install
        extracted.dirs()[0].copytree(destination)  # copy nested dir contents

    hookenv.status_set('maintenance', 'configuring insightedge')
    with host.chdir(destination):
        insightedge_jars = subprocess.check_output([
            'bash', '-c',
            '. {}; get_libs ,'.format(
                destination / 'sbin' / 'common-insightedge.sh'
            )
        ], env={'INSIGHTEDGE_HOME': destination}).decode('utf8')
    spark.register_classpaths(insightedge_jars.split(','))

    set_state('insightedge.installed')


@when('spark.ready')
@when('insightedge.installed')
def restart_services(spark):
    master_info = spark.get_master_info()
    master_url = master_info['connection_string']
    if data_changed('insightedge.master_url', master_url):
        master_ip = master_info['master']
        local_ip = utils.resolve_private_address(hookenv.unit_private_ip())
        is_master = master_ip == local_ip
        stop_datagrid_services()
        start_datagrid_services(master_url,
                                is_master,
                                not is_master or not spark.is_scaled())
    set_state('insightedge.ready')
    hookenv.status_set('active', 'ready')


def start_datagrid_services(master_url, is_master, is_slave):
    # TODO:
    #   * only start datagrid-master when on spark-master unit
    #   * only start datagrid-slave when on spark-slave unit
    #   * some of the below settings should be exposed as charm config
    if is_master:
        subprocess.call(["/usr/lib/insightedge/sbin/start-datagrid-master.sh",
                         "-m", "localhost",
                         "-s", "1G"])
    if is_slave:
        subprocess.call(["/usr/lib/insightedge/sbin/start-datagrid-slave.sh",
                         "--master", master_url,
                         "--locator", "localhost:4174",
                         "--group", "insightedge",
                         "--name", "insightedge-space",
                         "--topology", "2,0",
                         "--size", "1G",
                         "--instances", "id=1;id=2"])


def stop_datagrid_services():
    if utils.jps("insightedge.marker=master"):
        d = dict(os.environ)
        d["TIMEOUT"] = str(10)
        cmd = "/usr/lib/insightedge/sbin/stop-datagrid-master.sh"
        subprocess.call(cmd, shell=True, env=d)
    if utils.jps("insightedge.marker=slave"):
        cmd = "/usr/lib/insightedge/sbin/stop-datagrid-slave.sh"
        subprocess.call(cmd, shell=False)
