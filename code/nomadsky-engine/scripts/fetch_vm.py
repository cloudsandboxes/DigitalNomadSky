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
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import SubscriptionClient



# Use interactive browser login
tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
credential = InteractiveBrowserCredential(tenant_id=tenant_id)

# -------------------------------
# Find VM name in the entire environment
# -------------------------------
subscription_client = SubscriptionClient(credential)
vm_found = False

for sub in subscription_client.subscriptions.list():
    subscription_ids = sub.subscription_id
    compute_client = ComputeManagementClient(credential, subscription_ids)
    resource_client = ResourceManagementClient(credential, subscription_ids)
    network_client = NetworkManagementClient(credential, subscription_ids)

    
    vms = compute_client.virtual_machines.list_all()
    for vm in vms:
         if vm.name == vmname:
             print(f"VM '{vmname}' found!")
             # VM found
             vm_found = True
             # VM basic info
             vm_name = vm.name
             vm_size = vm.hardware_profile.vm_size
             os_type = vm.storage_profile.os_disk.os_type.value
             resource_id = vm.id
             subscription_id = subscription_ids
             resource_group  = resource_group_name




# Example: connect to Azure subscription
# List resource groups as a test
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
print(f"VM '{vmname}' found successfully in {source}! with resource_id = {resource_id}")
