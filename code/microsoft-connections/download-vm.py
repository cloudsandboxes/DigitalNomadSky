import requests
import time
import json
import os
from azure.identity import DefaultAzureCredential
from urllib.parse import urlparse

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient

   
    # -------------------------------
    # 3) REQUEST DISK EXPORT (ASYNC)
    # -------------------------------
    # print("\nRequesting disk export access...")
    export_uri = f"https://management.azure.com{os_disk_id}/beginGetAccess?api-version=2023-04-02"
    export_body = {
        "access": "Read",
        "durationInSeconds": 3600
    }
    
    headers = get_headers(credential)
    export_resp = requests.post(export_uri, headers=headers, json=export_body)
    export_resp.raise_for_status()
    
    # Get the async operation URL from Location or Azure-AsyncOperation header
    if "Location" in export_resp.headers:
        operation_url = export_resp.headers["Location"]
    elif "Azure-AsyncOperation" in export_resp.headers:
        operation_url = export_resp.headers["Azure-AsyncOperation"]
    else:
        raise Exception("No async operation URL found in response headers")
    
    print(f"Polling for SAS URL generation...")
    result = poll_async_operation(operation_url, credential, timeout=300)
    
    # The SAS URL should be in the result
    sas_url = result.get("properties", {}).get("output", {}).get("accessSAS")
    if not sas_url:
        # Try alternative location
        sas_url = result.get("accessSAS")
    
    if not sas_url:
        raise Exception(f"Could not find SAS URL in response: {result}")
    
    print("SAS URL obtained successfully.")
    
    # -------------------------------
    # 4) DOWNLOAD THE VHD
    # -------------------------------
    print(f"\nDownloading OS disk to {output_vhd_path}...")
    print("This may take a while depending on disk size...")
    
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
                    print(f"\rProgress: {percent:.1f}% ({downloaded / (1024**3):.2f} GB)", end="")
    
    print(f"\n\n✓ Download complete: {output_vhd_path}")
    
    # Get file size
    file_size_gb = os.path.getsize(output_vhd_path) / (1024**3)
    print(f"File size: {file_size_gb:.2f} GB")
    
    # -------------------------------
    # 5) REVOKE ACCESS (OPTIONAL)
    # -------------------------------
    print("\nRevoking disk access...")
    revoke_uri = f"https://management.azure.com{os_disk_id}/endGetAccess?api-version=2023-04-02"
    headers = get_headers(credential)
    revoke_resp = requests.post(revoke_uri, headers=headers)
    if revoke_resp.status_code in [200, 202]:
        print("Disk access revoked.")
    
    print("\n✓ All operations completed successfully!")
    print(f"\nNote: VM '{vm_name}' is deallocated. Start it again when needed.")

except requests.exceptions.RequestException as e:
    print(f"\n✗ HTTP Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
