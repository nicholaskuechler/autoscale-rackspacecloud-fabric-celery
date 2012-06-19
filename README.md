autoscale-rackspacecloud-fabric-celery
======================================

Auto-scale Rackspace Cloud servers with Fabric and Celery

Copyright 2012 Nicholas Kuechler
http://www.nicholaskuechler.com/


GETTING STARTED
===============

* You must edit auto-scale.py, fabfile.py, tasks.py, conf/settings.py to fit your project
* conf/settings.py
	* Set your Rackspace Cloud API details
		* CLOUDSERVERS_USERNAME, CLOUDSERVERS_API_KEY
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
	* Set the saved snapshot image template used to create new workers in: deploy_worker()
		* Currently: saved-worker-template
	* The deploy_worker() does most of the work


TO DO:
======

* Use conf/settings.py to define additional settings:
	* Code base path
	* Snapshot image template name
	* Paths to Fabric and fabfile.py in auto-scale.py
	* RabbitMQ vhost name
