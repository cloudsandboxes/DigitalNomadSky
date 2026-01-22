import sys
import json
from datetime import datetime, timezone
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging



# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()

if source == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      from fetching_vm import fetch_vm
          
      try:
            result = fetch_vm(vmname)
            print(json.dumps(result))
      except IndexError:
        raise Exception('something went wrong, the vm is not found in Azure!')   

elif source == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.


# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=bde21699-fbec-4be5-93ce-ee81109b211f"))
logger.setLevel(logging.INFO)

# Prepare JSON data
times = datetime.now(timezone.utc)
data = {
    "unique_id": unique_id,
    "step": "fetch-vm",
    "time": times,
    "message": f"VM found in '{source}'"
}

# Send as custom log
logger.info(data)




#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)

