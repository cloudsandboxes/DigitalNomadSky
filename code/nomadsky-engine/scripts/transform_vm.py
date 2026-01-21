import sys
import subprocess
import json

# Simulate fetching VM
# TODO: Add actual API calls to source platform here

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
      importdisktype = config.importdisktype
      if (importdisktype == exportdisktype):
            result = {
             'message': f"the diskfile type is already '{config.importdisktype}' so no need to transform type!",
             }
            print(json.dumps(result))
      else:
            result = {
             'message': f"the import diskfile type is different '{config.importdisktype}' to the export type '{exportfiletype}' so need to transform!",
             }
            print(json.dumps(result))
      
      
elif destination == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


#from helpers import my_function
#result = my_function(5)


#try:
#    subscription_id = vm_resource_id
#except IndexError:
#        raise Exception(f" Invalid resource ID format: '{vm_resource_id}' ")
    
