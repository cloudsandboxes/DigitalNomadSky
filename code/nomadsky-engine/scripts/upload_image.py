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

if destination == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      from upload_disk import upload_disk
          
      try:
            url = upload_disk(shared_data)
            result = {
             'message': f"the diskfile is succesfully transfered to '{destination}' at the '{url}'",
             'disk_url' : url
             }
            print(json.dumps(result))
      except IndexError:
        raise Exception(f" Invalid resource ID format: '{shared_data}' ")
   
elif destination == 'aws':
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
    "step": "upload-image",
    "time": times,
    "message": f"VM is uploaded to  '{destination}'"
}

# Send as custom log
logger.info(data)



#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)



