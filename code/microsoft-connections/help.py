import sys
import json
import os
import time
import requests
from datetime import datetime, timezone, timedelta
#from urllib.parse import urlparse

# Get arguments
source = 'azure'
destination = 'aws'
vmname = 'helpmij' 
subscription_id = '41aff5e1-41c9-4509-9fcb-d761d7f33740'
resource_group = 'test'
os_disk_id = '/subscriptions/41aff5e1-41c9-4509-9fcb-d761d7f33740/resourceGroups/test/providers/Microsoft.Compute/disks/helpmij_OsDisk_1_f5fd3ccab7494e1ab6409d83ce4b68df'
output_vhd_path = r"C:\Temp\osdisk.vhd"
file_size_gb = os.path.getsize(output_vhd_path) / (1024**3)
print(file_size_gb)
if file_size_gb > 1:
   result = {
      'message': f"VM '{vmname}' successfully downloaded from {source}!",
   }
   print(json.dumps(result))



from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.core.exceptions import HttpResponseError

#from azure.mgmt.network import NetworkManagementClient
# Use interactive browser login
tenant_id = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"
credential = InteractiveBrowserCredential(tenant_id=tenant_id)




# -------------------------------
# 3) REQUEST DISK EXPORT (ASYNC)
# -------------------------------
compute_client = ComputeManagementClient(credential, subscription_id)

# Generate SAS URL
# current UTC time, timezone-aware
now_utc = datetime.now(timezone.utc)
# example: 1 hour later
expiry_time = now_utc + timedelta(hours=1)

sas = compute_client.disks.begin_grant_access(
    resource_group_name=resource_group,
    disk_name=os_disk_id.split('/')[-1],
    grant_access_data={"access": "Read", "duration_in_seconds": 3600}
).result()
sas_url = sas.access_sas
print(sas_url)

    
    
# -------------------------------
# 4) DOWNLOAD THE VHD
# -------------------------------

from time import sleep



def download(output_vhd_path, sas_url):
   chunk_size = 50 * 1024 * 1024  # 50 MB per chunk
   max_retries = 5

   # Resume if file exists
   start_byte = os.path.getsize(output_vhd_path) if os.path.exists(output_vhd_path) else 0

   while True:
       headers = {"Range": f"bytes={start_byte}-"}
       try:
           with requests.get(sas_url, headers=headers, stream=True, timeout=60) as r:
               r.raise_for_status()
               mode = "ab" if start_byte > 0 else "wb"
               with open(output_vhd_path, mode) as f:
                   for chunk in r.iter_content(chunk_size=chunk_size):
                       if chunk:
                           f.write(chunk)
                           start_byte += len(chunk)
                           #print(f"Downloaded {start_byte / (1024*1024):.1f} MB", end="\r")
           break  # finished successfully
       except (requests.ConnectionError, requests.ChunkedEncodingError) as e:
           #print(f"\nConnection error, retrying... ({e})")
           sleep(5)  # wait a few seconds
           max_retries -= 1
           if max_retries <= 0:
               raise Exception("Max retries exceeded")

file_size_gb = os.path.getsize(output_vhd_path) / (1024**3)
if file_size_gb > 1:
   result = {
      'message': f"VM '{vmname}' successfully downloaded from {source}!",
   }
   print(json.dumps(result))
else: 
    download(output_vhd_path, sas_url)
    result = {
         'message': f"VM '{vmname}' successfully downloaded from {source}!",
       }

    print(json.dumps(result))
