# Auto-scale Rackspace Cloud servers with Fabric and Celery
#
# Copyright 2012 Nicholas Kuechler
# http://www.nicholaskuechler.com/

""" Fabric fabfile to build workers using Rackspace Cloud api and then configure them with the code base. """

import os
import sys
import datetime
import base64
import cloudservers
#import cloudlb
import urllib2
import time
import uuid

from time import sleep
from subprocess import call
from threading import Thread
from fabric.api import *
from conf import settings

env.colors = True
env.user = 'root'
env.connection_attempts = 3
env.timeout = 30
env.keepalive = 900

def _get_server_image(cs, image_name):
    i = cs.images.find(name=image_name)
    return i

def _get_flavor(cs, ram_size):
    return cs.flavors.find(ram=ram_size)

def _get_file_contents(file_name):
    contents = open(file_name, 'r').read()
    return contents

def _reboot_server(cs, s):
    """ reboot a cloud server """
    s.reboot()
    sleep(90)
    return True

def _create_server(cs, image_name, ram_size):
    now = datetime.datetime.now()

    get_uuid = uuid.uuid4()
    server_name = 'worker-%s' % (get_uuid)
    print 'Creating server %s' % server_name
    
    image = _get_server_image(cs, image_name)
    if not image:
        raise Exception('Could not get server image "%s"' % image_name)
    
    flavor = _get_flavor(cs, ram_size)
    if not flavor:
        raise Exception('Could not get flavor with %s ram' % ram_size)
    
    server = cs.servers.create(
        server_name,
        image,
        flavor,
    )

    return server

def _wait_for_server(cs, s, with_url_ping=False):
    while s.status != 'ACTIVE':
        sleep(60)
        s = cs.servers.get(s.id)
        print '%s: %s (%s%%)' % (s.id, s.status, s.progress)
    
    if with_url_ping:
        # Wait for a response
        url = 'http://%s/index.html' % s.public_ip
        tries = 0
        while True:
            try:
                print 'Attempting to connect to %s' % url
                urllib2.urlopen(url)
                print 'ping success, returning'
                break
            except urllib2.HTTPError, e:
                print e
                if e.code == 401:
                    print '401 not authorized'
                elif e.code == 404:
                    print '404 not found... waiting...'
                elif e.code == 503:
                    print '503 service unavailable'
                else:
                    print 'unknown error: %s' % e
                sleep(30)
            except urllib2.URLError, u:
                print u
                print 'Connection refused for now...'
                sleep(30)
            
            tries += 1
            if tries > 20: # 10 minutes
                raise Exception('URL ping timed out')

def _install_nginx():
    runcmd('aptitude -y install nginx')

def _restart_nginx():
    runcmd('/etc/init.d/nginx restart')

def _make_web_directory():
    runcmd('mkdir -p /var/www/')
    runcmd('echo "<html><body>hello</body></html>" > /var/www/index.html')

def _update_host():
    runcmd('aptitude -y update && aptitude -y safe-upgrade')

def _install_server_tools():
    # commonly used packages
    runcmd('aptitude -y install screen tcpdump dnsutils')
    # git / subversion packages
    runcmd('aptitude -y install git git-core subversion')

def start_celery_worker():
    _start_celery_worker()

def _start_celery_worker():
    """ start remote celery worker """
    runcmd('/etc/init.d/celeryd start')

def stop_celery_worker():
    _stop_celery_worker()

def _stop_celery_worker():
    """ stop remote celery worker """
    runcmd('/etc/init.d/celeryd stop')

def stop_celery_worker_test():
    """ stop remote celery worker """
    run('/etc/init.d/celeryd stop', pty=False)

def _set_up_iptables_locally(cs, s):
    # set up iptables
    # should probably be using local()
    call("/sbin/iptables -I INPUT 9 -s %s/32 -p tcp -m state --state NEW -m tcp --dport 3306 -j ACCEPT" % (s.private_ip), shell=True)
    call("/sbin/iptables -I INPUT 9 -s %s/32 -p tcp -m state --state NEW -m tcp --dport 5672 -j ACCEPT" % (s.private_ip), shell=True)

def _rsync_codebase_to_worker(cs, s):
    """ rsync code base to new worker """
    call("/usr/bin/rsync -e \"ssh -o StrictHostKeyChecking=no\" --quiet -av --delete /opt/codebase/ root@%s:/opt/codebase/" % (s.private_ip), shell=True)

@parallel
def create_multiple_workers():
    """ deploy new workers in parallel with python threads """

    for i in range(8):
        t = Thread(target = deploy_worker, args=(i,))
        t.start()

@parallel
def deploy_worker(thread_num):
    cs = cloudservers.CloudServers(settings.CLOUDSERVERS_USERNAME, settings.CLOUDSERVERS_API_KEY)
    s = _create_server(cs, settings.CLOUDSERVERS_IMAGE_TEMPLATE, 256)

    _wait_for_server(cs, s, with_url_ping=False)

    print '%d: %s: Server IP is %s (private: %s)' % (thread_num, s.id, s.public_ip, s.private_ip)

    # small delay to allow the server to fully boot up
    sleep(60)

    # set fabric's env.host_string so it knows what server we want to run commands on
    env.host_string = s.private_ip

    # set up iptables on the master server so that the workers can connect back to it
    _set_up_iptables_locally(cs, s)
    # rsync the code base to the new worker node
    _rsync_codebase_to_worker(cs, s)

    # reboot the newly created worker node
    print '%d: Rebooting: %s (id: %s)' % (thread_num, s.private_ip, s.id)
    _reboot_server(cs, s)
    sleep(90)

    # start the celery daemon on the new worker node
    print '%d: Starting celery worker: %s (id: %s)' % (thread_num, s.private_ip, s.id)
    env.host_string = s.private_ip
    _start_celery_worker()

    sleep(30)


# Helpers    
def runcmd(arg):
    if env.user != "root":
        sudo("%s" % arg, pty=True)
    else:
        run("%s" % arg, pty=True)



