import sys
import json
from datetime import datetime, timezone
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging


# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()
shareddata_json = sys.argv[4]
shared_data = json.loads(shareddata_json)
unique_id = sys.argv[5]

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
      # AWS SDK code to download VM
      sys.path.append(r"C:/projects/nomadsky/code/Amazon")
      import config
      from downloading_vm import  download_aws_osdisk
      try:
            result =  download_aws_osdisk(shared_data)
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" VM could not be downloaded: '{shared_data}' ")
else:
        raise Exception(f" the source platform is not yet supported")
      

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=bde21699-fbec-4be5-93ce-ee81109b211f"))
logger.setLevel(logging.INFO)

# Prepare JSON data
times = datetime.now(timezone.utc)
data = {
    "unique_id": unique_id,
    "step": "download-vm",
    "time": times,
    "message": f"VM downloaded from '{source}'"
}

# Send as custom log
logger.info(data)


#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)
