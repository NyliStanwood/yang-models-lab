import sys
import os
import subprocess
from ncclient import manager

script_name = os.path.basename(__file__)

if len(sys.argv) < 2:
    print("Error - Incorrect arguments")
    print('Usage: python', script_name, '<container_name>')
    print('Example: python', script_name, 'clab-srlinux-testbed-r1')
    exit(1)
else:
    container_name = sys.argv[1]
    check_container = subprocess.getoutput("docker ps -a | awk '{print $NF}' | grep " + container_name)

if check_container != container_name:
    print("Error - Incorrect arguments: You need to specify the container name of the network device.")
    print('Usage: python', script_name, '<container_name>')
    print('Example: python', script_name, 'clab-srlinux-testbed-r1')
    exit(1)
    
yang_server = {
    "host": container_name,
    "port": 830,
    "username": "admin",
    "password": "NokiaSrl1!",
    "hostkey_verify": False,
    "device_params": {"name": "default"}
}

session = manager.connect(**yang_server)

#print("Session ID: ", session.session_id)

# Create a filter
#  srl_nokia-interfaces@2026-07-31.yang

# module srl_nokia-interfaces {
#   yang-version 1.1;
#   namespace "urn:nokia.com:srlinux:chassis:interfaces";


schema_tree_filter = """
<interface xmlns="urn:nokia.com:srlinux:chassis:interfaces"/>
"""

# Execute the GET RPC
reply = session.get(filter=("subtree", schema_tree_filter))

print(reply)

session.close_session()


