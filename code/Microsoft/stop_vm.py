from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient
import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3]
shared_data_json = sys.argv[4]  # 4th argument
shared_data = json.loads(shared_data_json)
# Extract specific value
vm_resource_id = shared_data.get('resource_id', '')


def deallocate_vm(resource_id):
    """
    Deallocate an Azure VM given its full resource ID.
    Example resource_id:
    /subscriptions/<sub_id>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/<vm_name>
    """

    # Parse subscription_id, resource_group, and vm_name from resource ID
    parts = resource_id.strip("/").split("/")
    try:
        subscription_id = parts[1]
        resource_group = parts[3]
    except IndexError:
        raise Exception(f" Invalid resource ID format: '{resource_id}' ")
        return

    # Authenticate interactively
    tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)

    # Create compute client
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Deallocate the VM
    # print(f"Deallocating VM '{vmname}' in resource group '{resource_group}'...")
    async_vm_deallocate = compute_client.virtual_machines.begin_deallocate(resource_group, vmname)
    async_vm_deallocate.wait()  # Wait until deallocation is complete
    # print(f"VM '{vmname}' has been deallocated successfully!")

if __name__ == "__main__":
    deallocate_vm(vm_resource_id)
    result = {
      'message': f"VM '{vmname}' has been deallocated successfully!",
      'resource_id': vm_resource_id
    }
    print(json.dumps(result))



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


# Output success message (Flask will capture this)
# print(f"VM '{vmname}' deallocated successfully in {source}!")
