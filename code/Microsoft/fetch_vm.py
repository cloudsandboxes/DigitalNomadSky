import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()

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
from azure.mgmt.resource import SubscriptionClient
from azure.core.exceptions import HttpResponseError

# Use interactive browser login
tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
credential = InteractiveBrowserCredential(tenant_id=tenant_id)

# -------------------------------
# Find VM name in the entire environment
# -------------------------------
subscription_client = SubscriptionClient(credential)
vm_found = False

for sub in subscription_client.subscriptions.list():
        try:
            subscription_ids = sub.subscription_id
            compute_client = ComputeManagementClient(credential, subscription_ids)
            resource_client = ResourceManagementClient(credential, subscription_ids)
            vms = compute_client.virtual_machines.list_all()
            for vm in vms:
                if vm.name.lower() == vmname:
                     # print(f"VM '{vmname}' found!")
                     # VM found
                     vm_found = True
             
                     # VM basic info
                     resource_group  = vm.id.split("/")[4]
                     full_vm = compute_client.virtual_machines.get(resource_group, vmname, expand="instanceView")
                     vm_size = vm.hardware_profile.vm_size
                     os_type = full_vm.storage_profile.os_disk.os_type
                     resource_id = vm.id
                     subscription_id = subscription_ids
                     power_state  = full_vm.instance_view.statuses
                     os_disk_id = vm.storage_profile.os_disk.managed_disk.id
                     # os_type =   full_vm.storage_profile.os_disk.os_type.value
                        
        except HttpResponseError as e:
            # print(f"Skipping subscription {sub.subscription_id}: {e.message}")
            continue

if not vm_found:
    raise Exception(f"VM '{vmname}' not found in {source}")
else:
    # Output success message (Flask will capture this)
    # print(f"VM '{vmname}' found successfully in {source}! with resource_id = {resource_id}")
    # way to export multiple values
    # print(json.dumps({"output1": f"VM '{vmname}' found successfully in {source}! with resource_id = {resource_id}", "output2": subscription_id}))
    result = {
      'message': f"VM '{vmname}' found successfully in {source}!",
      'vm_size': vm_size,
      'resource_id': resource_id,
      'resource_group': resource_group,
      'subscription_id': subscription_id,
      'os_disk_id' : os_disk_id,
      'vm_name' : vmname
    }

print(json.dumps(result))
