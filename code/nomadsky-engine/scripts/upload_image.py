import sys
from azure.identity import InteractiveBrowserCredential
from azure.mgmt.compute import ComputeManagementClient
import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()
shareddata_json = sys.argv[4]
shared_data = json.loads(shareddata_json)

exportdisktype = shared_data.get('exportdisktype', '')

if destination == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      from upload-disk import upload_disk
      importdisktype = config.importdisktype
    
      try:
            result = {
             'message': f"the diskfile type is already '{config.importdisktype}' so no need to transform type!",
             }
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" Invalid resource ID format: '{shared_data}' ")
   
elif destination == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


#from helpers import my_function
#result = my_function(5)




