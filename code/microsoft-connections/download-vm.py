import sys
import json
import os
import time
from time import sleep
import requests
from datetime import datetime, timedelta, timezone

# Get arguments
source = sys.argv[1]
destination = sys.argv[2]
vmname = sys.argv[3].lower()
shared_data_json = sys.argv[4]  # 4th argument
shared_data = json.loads(shared_data_json)
# Extract specific value
subscription_id = shared_data.get('subscription_id', '')
resource_group = shared_data.get('resource_group', '')
os_disk_id = shared_data.get('os_disk_id', '')
output_vhd_path = r"C:\Temp\osdisk.vhd"



from azure.identity import InteractiveBrowserCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.core.exceptions import HttpResponseError
  

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
#print(sas_url)

# -------------------------------
# 4) DOWNLOAD THE VHD
# -------------------------------


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

#try
#file_size_gb = os.path.getsize(output_vhd_path) / (1024**3)
#if file_size_gb > 1:
#   result = {
#      'message': f"VM '{vmname}' successfully downloaded from {source}!",
#   }
#   print(json.dumps(result))
#else: 
    
download(output_vhd_path, sas_url)
result = {
      'message': f"VM '{vmname}' successfully downloaded from {source}!",
     }

print(json.dumps(result))







"""    
    file_size_gb = os.path.getsize(output_vhd_path) / (1024**3)

#print(f"File size: {file_size_gb:.2f} GB")
    
    # -------------------------------
    # 5) REVOKE ACCESS (OPTIONAL)
    # -------------------------------
    #print("\nRevoking disk access...")
    revoke_uri = f"https://management.azure.com{os_disk_id}/endGetAccess?api-version=2023-04-02"
    headers = get_headers(credential)
    revoke_resp = requests.post(revoke_uri, headers=headers)
    if revoke_resp.status_code in [200, 202]:
        #print("Disk access revoked.")
    
    #print("\n✓ All operations completed successfully!")
    #print(f"\nNote: VM '{vm_name}' is deallocated. Start it again when needed.")

except requests.exceptions.RequestException as e:
    print(f"\n✗ HTTP Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

sas_url= "happy"
if not sas_url:
    raise Exception(f"VM '{vmname}' not found in {source}")
else:
    # Output success message (Flask will capture this)
    # print(f"VM '{vmname}' found successfully in {source}! with resource_id = {resource_id}")
    # way to export multiple values
    # print(json.dumps({"output1": f"VM '{vmname}' found successfully in {source}! with resource_id = {resource_id}", "output2": subscription_id}))
    result = {
      'message': f"VM '{vmname}' successfully downloaded from {source}!",
    }

print(json.dumps(result))

# 'output_vdh': output_vhd_path,
#      'filesize' : file_size_gb
"""
