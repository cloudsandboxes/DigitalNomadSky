import sys
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient
import sys

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3]
vm_resource_id = sys.argv[4]


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
        vm_name = parts[7]
    except IndexError:
        print("Invalid resource ID format")
        return

    # Authenticate interactively
    credential = InteractiveBrowserCredential()

    # Create compute client
    compute_client = ComputeManagementClient(credential, subscription_id)

    # Deallocate the VM
    print(f"Deallocating VM '{vm_name}' in resource group '{resource_group}'...")
    async_vm_deallocate = compute_client.virtual_machines.begin_deallocate(resource_group, vm_name)
    async_vm_deallocate.wait()  # Wait until deallocation is complete
    print(f"VM '{vm_name}' has been deallocated successfully!")

if __name__ == "__main__":
    deallocate_vm(vm_resource_id)
    



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
