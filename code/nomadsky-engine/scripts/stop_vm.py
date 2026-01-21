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
      result = subprocess.run(
        ['python', 'C:/Projects/nomadsky/code/Microsoft/stop_vm.py', source, destination, vmname, shareddata_json],
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
