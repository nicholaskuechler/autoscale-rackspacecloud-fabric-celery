# Rackspace Cloud details
CLOUDSERVERS_USERNAME = "RACKSPACE_CLOUD_USERNAME"
CLOUDSERVERS_API_KEY = "RACKSPACE_CLOUD_API_KEY"
CLOUDSERVERS_DATA_CENTER = "dfw"

# The codebase path that will be rsync'd over to newly created workers
CODEBASE_PATH = "/opt/codebase"

# The saved image template backup to use to build new workers
CLOUDSERVERS_IMAGE_TEMPLATE = "saved-worker-template"

# TMP file for auto-scale.py, used to determine if we have already scaled up or not
AUTOSCALE_TMP_FILE = "/tmp/auto-scale.tmp"
