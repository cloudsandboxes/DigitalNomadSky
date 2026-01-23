import sys
import subprocess
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
exportdisktype = shared_data.get('exportdisktype', '')
unique_id = sys.argv[5]

# Using a set (fastest for membership testing)
def check_value(value, allowed_values={1, 2, 3}):
    return value in allowed_values


if destination == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      importdisktype = config.importdisktype
      if exportdisktype in importdisktype:
        result = {
             'message': f"the diskfile type is already '{config.importdisktype}' so no need to transform type!",
             }
        print(json.dumps(result))
      else:
            importdisktype = importdisktype[0]
            #do qemu to convert the current disk(export) to the outputformat (importdisktype).
            #subprocess.run([qemu_path, "convert", "-O", output_format, os_disk_path, output_disk_path], check=True)
            (result add = new_diskpath = output_disk_path)
            result = {
             'message': f"the import diskfile type is different '{config.importdisktype}' to the export type '{exportfiletype}' so need to transform!",
             }
            print(json.dumps(result))
       
elif destination == 'aws':
   a='empty'
   #     # AWS boto3 code to find VM
   # etc.



# -------------------------------
# 4) TRANSFORM OS DISK USING QEMU
# -------------------------------
#output_disk_path = os.path.splitext(os_disk_path)[0] + f".{output_format}"
#print(f"Transforming {os_disk_path} -> {output_disk_path} ...")
#subprocess.run([qemu_path, "convert", "-O", output_format, os_disk_path, output_disk_path], check=True)
#print(f"Disk conversion complete: {output_disk_path}")




#from helpers import my_function
#result = my_function(5)


#try:
#    subscription_id = vm_resource_id
#except IndexError:
#        raise Exception(f" Invalid resource ID format: '{vm_resource_id}' ")
    



# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=bde21699-fbec-4be5-93ce-ee81109b211f"))
logger.setLevel(logging.INFO)

# Prepare JSON data
times = datetime.now(timezone.utc)
data = {
    "unique_id": unique_id,
    "step": "transform",
    "time": times,
    "message": f"VM disk transformed to format from '{destination}'"
}

# Send as custom log
logger.info(data)
