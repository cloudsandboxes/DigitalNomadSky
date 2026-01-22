import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()
shareddata_json = sys.argv[4]
shared_data = json.loads(shareddata_json)

if source == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      from downloading_vm import download_vm
      try:
            result = download_vm(shared_data)
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" VM could not be downloaded: '{shared_data}' ")
   
elif source == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)
