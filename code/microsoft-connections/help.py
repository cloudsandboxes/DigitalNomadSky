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


with requests.get(sas_url, stream=True) as r:
    r.raise_for_status()
    with open(output_vhd_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=10_000_000):
            if chunk:
                f.write(chunk)

print("Download complete!")

result = {
      'message': f"VM '{vmname}' successfully downloaded from {source}!",
    }

print(json.dumps(result))

"""




from azure.storage.blob import BlobClient





blob = BlobClient.from_blob_url(sas_url)

with open(output_vhd_path, "wb") as f:
    download_stream = blob.download_blob()
    download_stream.readinto(f)


print("Download complete!")

result = {
      'message': f"VM '{vmname}' successfully downloaded from {source}!",
    }

print(json.dumps(result))

"""

    
    #print(f"\nDownloading OS disk to {output_vhd_path}...")
    #print("This may take a while depending on disk size...")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_vhd_path), exist_ok=True)
    
    vhd_resp = requests.get(sas_url, stream=True)
    vhd_resp.raise_for_status()
    
    # Get file size if available
    total_size = int(vhd_resp.headers.get('content-length', 0))
    downloaded = 0
    
    with open(output_vhd_path, "wb") as f:
        for chunk in vhd_resp.iter_content(chunk_size=1024*1024):  # 1MB chunks
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    #print(f"\rProgress: {percent:.1f}% ({downloaded / (1024**3):.2f} GB)", end="")
    
    #print(f"\n\n✓ Download complete: {output_vhd_path}")
    
    # Get file size
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
