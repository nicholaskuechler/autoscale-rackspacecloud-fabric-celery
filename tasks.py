# Auto-scale Rackspace Cloud servers with Fabric and Celery
#
# Copyright 2012 Nicholas Kuechler
# http://www.nicholaskuechler.com/

""" Celery tasks file """

from celery.task import task

""" Example task: add """


@task
def add(x, y):
    return x + y
