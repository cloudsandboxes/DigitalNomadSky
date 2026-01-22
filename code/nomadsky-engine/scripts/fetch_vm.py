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
            vmname,f,df,d,f,f,f,d = fetch_vm(vmname)
            result = {
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



import sys
import subprocess
# fetching VM

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()

if source == 'azure':
      # Azure SDK code to find VM
      import fetch_vm from fetching_vm  
      result = subprocess.run(
        ['python', 'C:/Projects/nomadsky/code/Microsoft/fetch_vm.py', source, destination, vmname],
        capture_output=True,
        text=True,
        check=True
      )
      output = result.stdout
      print(result.stdout)
      # Get the output
elif source == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.
