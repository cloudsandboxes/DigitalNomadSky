import sys

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3]

# Your logic here to fetch VM from source platform
# Example: connect to Azure/AWS/GCP API and search for the VM
# placeholder for actual implementation

# Simulate fetching VM
# TODO: Add actual API calls to source platform here
# if source == 'azure':
#     # Azure SDK code to find VM
# elif source == 'aws':
#     # AWS boto3 code to find VM
# etc.

# if vm_not_found:
#    raise Exception(f"VM '{vmname}' not found in {source}")

from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient

# Use interactive browser login
tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
credential = InteractiveBrowserCredential(tenant_id=tenant_id)

# Example: connect to Azure subscription
subscription_id = "41aff5e1-41c9-4509-9fcb-d761d7f33740"
client = ResourceManagementClient(credential, subscription_id)

# List resource groups as a test
for rg in client.resource_groups.list():
    print(rg.name)

# from azure.identity import DefaultAzureCredential
# from azure.mgmt.compute import ComputeManagementClient

# credential = DefaultAzureCredential()
# compute_client = ComputeManagementClient(credential, subscription_id)

# Search for VM
# vms = compute_client.virtual_machines.list_all()
#for vm in vms:
#    if vm.name == vmname:
 #       print(f"VM '{vmname}' found!")


# Output success message (Flask will capture this)
print(f"VM '{vmname}' found successfully in {source}!")
