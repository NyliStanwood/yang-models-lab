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

#print ("\nSession ID: ", session.session_id)

# Extract the NETCONF capabilities
capabilities = session.server_capabilities

yang_module_name = ""
yang_module_revision = ""
yang_module_number = 0

"""
Retrieve the set of YANG modules supported by the network device and save the schema representation of 
the regarding YANG data model files.
"""
print("\nRetrieving and downloading the YANG models supported by the network device "+ container_name + " ... \n")
for capability_key in capabilities:
    capability = capabilities[capability_key]
    if "module" in capability.parameters:
        yang_module_name = capability.parameters['module']
        yang_module_number = yang_module_number + 1

        if "revision" in capability.parameters:
            yang_module_revision = capability.parameters['revision'] 
            # Execute the get-schema RPC to get the schema of a particular YANG module
            schema = session.get_schema(identifier=yang_module_name, version=yang_module_revision)
            print("Downloading YANG model" + " " + str(yang_module_number) + ": " + str(capability.parameters))
            print("")
            # Save the YANG module schema as a YANG model file
            if not os.path.exists("yang-models-srlinux"):
                os.makedirs("yang-models-srlinux")
            with open("./yang-models-srlinux/{0}@{1}.yang".format(yang_module_name, yang_module_revision), 'w') as file:
                file.write(schema.data)
        else:
            yang_module_revision = None
            # Execute the get-schema RPC to get the schema of a particular YANG module
            schema = session.get_schema(identifier=yang_module_name, version=yang_module_revision)
            print("Downloading YANG model" + " " + str(yang_module_number) + ": " + str(capability.parameters)) 
            print("")
            # Save the YANG module schema as a YANG model file
            if not os.path.exists("yang-models-srlinux"):
                os.makedirs("yang-models-srlinux")
            with open("./yang-models-srlinux/{0}.yang".format(yang_module_name), 'w') as file:
                file.write(schema.data)

session.close_session()