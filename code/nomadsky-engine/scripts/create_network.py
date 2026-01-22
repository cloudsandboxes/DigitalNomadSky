import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()
shareddata_json = sys.argv[4]
shared_data = json.loads(shareddata_json)

if destination == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      from create_network import create_network
          
      try:
            nic = create_network(shared_data)
            result = {
             'message': f"the vnet and nic are succesfully created in '{destination}'!",
             'nic_id' : nic
             }
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" the vnet and/nic are not created.")
   
elif destination == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)




