# Auto-scale Rackspace Cloud servers with Fabric and Celery
#
# Copyright 2012 Nicholas Kuechler
# http://www.nicholaskuechler.com/

""" Auto Scale with Fabric, based on rabbitmq queue size """

import os
import sys
import subprocess
from time import sleep
from conf import settings

def get_rabbitmq_queue_size():
    """ Check rabbitmq queue """
    p1 = subprocess.Popen(["/usr/sbin/rabbitmqctl", "list_queues", "-p", "project_vhost"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["/bin/grep", "celery"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["/bin/grep", "-vv", "worker"], stdin=p2.stdout, stdout=subprocess.PIPE)
    p4 = subprocess.Popen(["/usr/bin/awk", "{print $2}"], stdin=p3.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    rabbitmq_output = p4.communicate()[0]
    rabbitmq_output = int(rabbitmq_output.rstrip())
    return rabbitmq_output

def start_workers_with_fabric():
    """ testing spinning up workers using fabric """
    tmp_file = open(settings.AUTOSCALE_TMP_FILE, 'w')
    tmp_file.write('running')
    tmp_file.close()
    subprocess.call("/usr/local/bin/fab -f /opt/codebase/auto-scale/fabfile.py create_multiple_workers", shell=True)
    return True

def check_if_workers_running():
    """ Check if we already have workers up and running by seeing if the temporary file exists"""
    if os.path.isfile(settings.AUTOSCALE_TMP_FILE):
        return True
    else:
        return False

def shutdown_and_destroy_workers_with_fabric():
    """ Use Fabric to shut down celery on workers and then destroy them. """
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
    elif queue_size = 0 and check_if_workers_running():
        print "queue size = 0 and workers already running. Spinning down and destroying workers."
        #shutdown_and_destroy_workers_with_fabric()
    else:
        print "queue size = 0. not doing anything."

if __name__ == "__main__":
    main()

