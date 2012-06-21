# Auto-scale Rackspace Cloud servers with Fabric and Celery
#
# Copyright 2012 Nicholas Kuechler
# http://www.nicholaskuechler.com/

"""
Clean up celery worker servers we no longer need
"""

import os
import sys
import subprocess
import cloudservers
from time import sleep
from conf import settings

cloudservers = cloudservers.CloudServers(settings.CLOUDSERVERS_USERNAME, settings.CLOUDSERVERS_API_KEY)
name = settings.WORKER_PREFIX
servers = cloudservers.servers.list()

""" Delete the servers from Rackspace Cloud """

i = 0
for s in servers:
    if name in s.name:
        print "Shutting down celery workers on %s - %s" % (s.name, s.private_ip)
        subprocess.call("/usr/local/bin/fab -f /opt/codebase/auto-scale/fabfile.py -H " + s.private_ip + " stop_celery_worker", shell=True)
        sleep(60)
        #print "Server: %-20s ==> Host: %-40s" % (s.name, s.hostId)
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
    print "File %s does not exist. Already deleted." % (settings.AUTOSCALE_TMP_FILE)

