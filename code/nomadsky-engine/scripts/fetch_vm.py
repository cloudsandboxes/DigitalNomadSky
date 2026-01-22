import sys
import json

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()

if destination == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      from fetching_vm import fetch_vm
          
      try:
            results = fetch_vm(vmname)
            results = {
             'message': f"the VM '{vmname}' has started succesfully in '{destination}'!",
             'vmname'; f      
             }
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" something went wrong the vm is not created.")
   
elif destination == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)
