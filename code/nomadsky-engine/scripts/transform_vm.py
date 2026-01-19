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

except IndexError:
        raise Exception(f" Invalid resource ID format: '{vm_resource_id}' ")
        
# Authenticate interactively
tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
#credential = InteractiveBrowserCredential(tenant_id=tenant_id)



#add logic



result = {
   'message': f"VM '{vmname}' has been changed the osdiskformat successfully!",
   'resource_id': vm_resource_id
    }
print(json.dumps(result))




