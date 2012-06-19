# Auto-scale Rackspace Cloud servers with Fabric and Celery
#
# Copyright 2012 Nicholas Kuechler
# http://www.nicholaskuechler.com/

""" Celery tasks file """

from celery.task import task

import os
import re
import sys
import ast
import math
import time
import socket
import string
import optparse
import datetime
import commands
import subprocess

""" Example task: add """
@task
def add(x, y):
    return x + y

