autoscale-rackspacecloud-fabric-celery
======================================

Auto-scale Rackspace Cloud servers with Fabric and Celery

Copyright 2012 Nicholas Kuechler
http://www.nicholaskuechler.com/


GETTING STARTED
===============

* You must edit auto-scale.py, fabfile.py, tasks.py, and conf/settings.py to fit your project
* conf/settings.py
	* Set your Rackspace Cloud API details
		* CLOUDSERVERS_USERNAME, CLOUDSERVERS_API_KEY
	* Set CLOUDSERVERS_IMAGE_TEMPLATE to the name of your Cloud Servers saved image backup snapshot
* auto-scale.py
	* Set your rabbitmq vhost details in: get_rabbitmq_queue_size()
		* Currently: project_vhost
	* Set the path to fabric and your fabfile.py in: start_workers_with_fabric()
		* Currently: /opt/codebase/auto-scale/fabfile.py
* fabfile.py
	* Set your new worker naming convention in: _create_server()
		* Currently: server_name = 'worker-%s' % (get_uuid)
	* Set path to your codebase that will rsync to new worker in: _rsync_codebase_to_worker()
		* Currently: /opt/codebase/ in the call() to rsync
	* The deploy_worker() does most of the work


TO DO:
======

* Use conf/settings.py to define additional settings:
	* Code base path
	* Snapshot image template name
	* Paths to Fabric and fabfile.py in auto-scale.py
	* RabbitMQ vhost name


READ MORE:
==========

Read my blog post on this project:

http://nicholaskuechler.com/2012/06/19/auto-scale-rackspace-cloud-servers-with-fabric-and-celery/
