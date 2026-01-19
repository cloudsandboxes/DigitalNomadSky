import sys
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient
import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3]

# Extract specific value from previous files
shared_data_json = sys.argv[4]  # 4th argument
shared_data = json.loads(shared_data_json)
vm_resource_id = shared_data.get('resource_id', '')

try:
    subscription_id = vm_resource_id
    resource_group = parts[3]
except IndexError:
        raise Exception(f" Invalid resource ID format: '{vm_resource_id}' ")
        return
# Authenticate interactively
tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
#credential = InteractiveBrowserCredential(tenant_id=tenant_id)



#add logic



result = {
   'message': f"VM '{vmname}' has been downloaded successfully!",
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
print(f"VM '{vmname}' found successfully in {source}!")
