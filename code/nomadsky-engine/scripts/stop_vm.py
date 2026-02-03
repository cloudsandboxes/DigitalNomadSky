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
      # Azure SDK code to stop VM
      sys.path.append(r"C:/projects/digitalnomadsky/code/Microsoft")
      import config
      from stopping_vm import stop_vm
          
      try:
            result = stop_vm(shared_data)
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" Invalid resource ID format: '{shared_data}' ")

elif source == 'cyso':
      # cyso SDK code to stop VM
      sys.path.append(r"C:/projects/digitalnomadsky/code/Cyso")
      import config
      from stopping_vm import stop_vm
          
      try:
            result = stop_vm()
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" Invalid resource ID format: '{shared_data}' ")

elif source == 'leaf':
      # leaf SDK code to stop VM
      sys.path.append(r"C:/projects/digitalnomadsky/code/Leafcloud")
      import config
      from stopping_vm import stop_vm
          
      try:
            result = stop_vm()
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" Invalid resource ID format: '{shared_data}' ")
   
elif source == 'aws':
      # AWS SDK code to stop VM
      sys.path.append(r"C:/projects/digitalnomadsky/code/Amazon")
      import config
      from stopping_vm import stop_aws_vm
          
      try:
            result = stop_aws_vm(shared_data)
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" Invalid resource ID format: '{shared_data}' ")

elif source == 'huawei':
      # Huawei SDK code to stop VM
      sys.path.append(r"C:/projects/digitalnomadsky/code/Huawei")
      import config
      from stopping_vm import stop_huawei_vm
          
      try:
            result = stop_huawei_vm(shared_data)
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" Invalid resource ID format: '{shared_data}' ")
else:
      raise Exception(f" The source platform is not yet supported: '{source}' ")

# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=bde21699-fbec-4be5-93ce-ee81109b211f"))
logger.setLevel(logging.INFO)

# Prepare JSON data
times = datetime.now(timezone.utc)
data = {
    "unique_id": unique_id,
    "step": "stop-vm",
    "time": times,
    "message": f"VM stopped in '{source}'"
}

# Send as custom log
logger.info(data)

#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)



