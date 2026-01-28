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
importdisktype = shared_data.get('importdisktype', '')
unique_id = sys.argv[5]
output_disk_path= r"C:\temp\output"

if exportdisktype == importdisktype:
        result = {
             'message': f"the diskfile type is already '{importdisktype}' so no need to transform type!", 
             }
else:
            #do qemu to convert the current disk(export) to the outputformat (importdisktype).
            #subprocess.run([qemu_path, "convert", "-O", output_format, os_disk_path, output_disk_path], check=True)
            #(result add = new_diskpath = output_disk_path)
            result = {
             'message': f"the import diskfile type is different '{importdisktype}' to the export type '{exportdisktype}' so need to transform!",
             }
print(json.dumps(result))




# -------------------------------
# 4) TRANSFORM OS DISK USING QEMU
# -------------------------------
#output_disk_path = os.path.splitext(os_disk_path)[0] + f".{output_format}"
#print(f"Transforming {os_disk_path} -> {output_disk_path} ...")
#subprocess.run([qemu_path, "convert", "-O", output_format, os_disk_path, output_disk_path], check=True)
#print(f"Disk conversion complete: {output_disk_path}")




#from helpers import my_function
#result = my_function(5)

   



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
