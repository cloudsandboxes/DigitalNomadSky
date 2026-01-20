import sys
# Simulate fetching VM
# TODO: Add actual API calls to source platform here

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()

if source == 'azure':
      # Azure SDK code to find VM
      result = subprocess.run(
      ['python', 'C:/projects/nomadsky/code/Microsoft-connections/fetch.py', source, destination, vmname],
      capture_output=True,
      text=True,
      check=True
      )
      output = result.stdout
      print(result)
      # Get the output
elif source == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.
