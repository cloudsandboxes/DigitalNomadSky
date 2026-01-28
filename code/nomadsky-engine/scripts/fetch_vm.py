import sys
import json
from datetime import datetime, timezone
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()
unique_id = sys.argv[5]


if source == 'azure':
      # Azure SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
      import config
      from fetching_vm import fetch_vm
          
      try:
            result = fetch_vm(vmname)
      except IndexError:
        raise Exception('something went wrong, the vm is not found in Azure!')   

elif source == 'cyso':
      # cyso openstack SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Cyso")
      import config
      from fetching_vm import fetch_vm
          
      try:
            result = fetch_vm()
      except IndexError:
        raise Exception('something went wrong, the vm is not found in Cyso Cloud!')  

elif source == 'aws':
      # Amazon SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Amazon")
      import config
      from fetching_vm import search_ec2_instance
          
      try:
            result = search_ec2_instance(vmname)
      except IndexError:
        raise Exception('something went wrong, the vm is not found in AWS!')  

elif source == 'huawei':
      # huawei SDK code to find VM
      sys.path.append(r"C:/projects/nomadsky/code/Huawei")
      import config
      from fetching_vm import search_huawei_vm
          
      try:
            result = search_huawei_vm(vmname)
      except IndexError:
        raise Exception('something went wrong, the vm is not found in Huawei Cloud!')  
else:
      raise Exception('something went wrong, the source cloud platform is not supported!')  


# -----
#Find optimal disktypeformat
# ------

sys.path.append(r"C:/projects/nomadsky/code/Vendor_Agnostic")
from general_parameters import preferred_type

def find_best_format(source_platform, destination_platform):
    source_exports = preferred_type[source_platform]["export"]
    destination_imports = preferred_type[destination_platform]["import"]

    # Try to find a matching format
    for fmt in source_exports:
        if fmt in destination_imports:
            return fmt, fmt

    # Fallback: first export + first import
    return source_exports[0], destination_imports[0]

exportdisktype,importdisktype = find_best_format(source,destination)
result["exportdisktype"]= exportdisktype
result["importdisktype"]= importdisktype
print(json.dumps(result)) 

#---------------------
#logs for research purpose
#----------------------
# Setup logger
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(connection_string="InstrumentationKey=bde21699-fbec-4be5-93ce-ee81109b211f"))
logger.setLevel(logging.INFO)

# Prepare JSON data
data = {
    "unique_id": unique_id,
    "step": "fetch-vm",
    "message": f"VM found in '{source}'"
}

# Send as custom log
logger.info(data)








#from helpers import my_function
#result = my_function(5)
#exportdisktype = shared_data.get('exportdisktype', '')
#a, b = my_function(10)

