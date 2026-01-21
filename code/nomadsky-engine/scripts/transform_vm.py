import sys
import subprocess

# Simulate fetching VM
# TODO: Add actual API calls to source platform here

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()
shareddata_json = sys.argv[4]

if source == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/microsoft-connections")
      import config
      
      result = {
            'message': f"VM '{config.tenantid}' has been deallocated successfully!",
       }
      print(json.dumps(result))
elif source == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


#from helpers import my_function
#result = my_function(5)
