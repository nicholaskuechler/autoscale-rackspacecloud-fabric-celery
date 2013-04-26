# Auto-scale Rackspace Cloud servers with Fabric and Celery
#
# Copyright 2012 Nicholas Kuechler
# http://www.nicholaskuechler.com/

""" Auto Scale with Fabric, based on rabbitmq queue size """

import os
import subprocess
import cloudservers
from time import sleep
from conf import settings


def get_rabbitmq_queue_size():
    """ Check rabbitmq queue """
    p1 = subprocess.Popen(["/usr/sbin/rabbitmqctl",
                           "list_queues",
                           "-p",
                           "%s" % settings.RABBITMQ_VHOST],
                          stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["/bin/grep", "celery"],
                          stdin=p1.stdout,
                          stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["/bin/grep", "-vv", "worker"],
                          stdin=p2.stdout,
                          stdout=subprocess.PIPE)
    p4 = subprocess.Popen(["/usr/bin/awk", "{print $2}"],
                          stdin=p3.stdout,
                          stdout=subprocess.PIPE)
    p1.stdout.close()
    rabbitmq_output = p4.communicate()[0]
    rabbitmq_output = int(rabbitmq_output.rstrip())
    return rabbitmq_output


def start_workers_with_fabric():
    """ testing spinning up workers using fabric """
    tmp_file = open(settings.AUTOSCALE_TMP_FILE, 'w')
    tmp_file.write('running')
    tmp_file.close()
    subprocess.call("/usr/local/bin/fab \
                    -f /opt/codebase/auto-scale/fabfile.py \
                    create_multiple_workers",
                    shell=True)
    return True


def check_if_workers_running():
    """ Check if we already have workers up and running """
    """ See if the temporary file exists """
    if os.path.isfile(settings.AUTOSCALE_TMP_FILE):
        return True
    else:
        return False


def shutdown_and_destroy_workers():
    """ Use Fabric to shut down celery on workers then destroy them """

    cloudservers = cloudservers.CloudServers(settings.CLOUDSERVERS_USERNAME,
                                             settings.CLOUDSERVERS_API_KEY)
    name = settings.WORKER_PREFIX
    servers = cloudservers.servers.list()

    """ Use Fabric to shut down celery daemon on the workers """
    for s in servers:
        if name in s.name:
            print "Shutting down celery workers on %s - %s" % (s.name,
                                                               s.private_ip)
            subprocess.call("/usr/local/bin/fab \
                            -f /opt/codebase/auto-scale/fabfile.py \
                            -H " + s.private_ip + " stop_celery_worker",
                            shell=True)

    # Sleep for 600 seconds
    # Allows time for all celery workers to finish processing their tasks
    sleep(600)

    """ Delete the servers from Rackspace Cloud """
    i = 0
    for s in servers:
        if name in s.name:
            print "DELETING server: %-20s" % (s.name)
            s.delete()
            i += 1

    """ Restart networking to clear iptables policies """
    if i > 0:
        print "Restarting networking to clear iptables policies"
        subprocess.call(["/etc/init.d/networking", "restart"])
    else:
        print "No workers found or deleted. Not restarting networking."

    """ Delete the temporary file """
    try:
        os.remove(settings.AUTOSCALE_TMP_FILE)
    except:
        print "File %s does not exist." % (settings.AUTOSCALE_TMP_FILE)

    return True


def main():
    queue_size = get_rabbitmq_queue_size()
    print "queue size: %d" % (queue_size)
    if check_if_workers_running():
        print "workers already running"
    else:
        print "workers not running"
    if queue_size > 0 and not check_if_workers_running():
        print "queue size > 0 and no workers running. starting workers."
        start_workers_with_fabric()
    elif queue_size > 0 and check_if_workers_running():
        print "queue size > 0 and workers already running"
    elif queue_size == 0 and check_if_workers_running():
        print "queue size = 0 and workers already running. " \
              "Spinning down and destroying workers."
        shutdown_and_destroy_workers()
    else:
        print "queue size = 0. not doing anything."

if __name__ == "__main__":
    main()
