
#!/usr/bin/env python3
def export_os_disk(vm_name):
   """
   stackit.cloud OpenStack VM Access Script
   This script authenticates to stackit.cloud OpenStack and downloads the image
   """
    
   import os
   import sys
   import webbrowser
   from stackit.core.configuration import Configuration
   from stackit.iaas.api.default_api import DefaultApi
   from stackit.sdk.configuration import Configuration
   import getpass
   import json
   sys.path.append(r"C:/projects/digitalnomadsky/code/Stackit")
   import tkinter as tk
   from tkinter import filedialog
   import time
   import requests
   from requests.exceptions import ConnectionError, ChunkedEncodingError

   # Get arguments
   source = sys.argv[1]
   destination = sys.argv[2]
   vm_name = sys.argv[3].lower()
   import config
   output_path= fr"C:\Temp\osdisk-{vm_name}.qcow2"
   chunk_size = 50 * 1024 * 1024  # 50 MB per chunk

   if os.path.exists(output_path):
               result = {
                  'message': f"VM {vm_name} already downloaded from {source}!",
                  'output_path' : output_path
                 }
               return result



      
   # Step 1: Get credentials
   #print("\n[1/4] Getting credentials...")
   # Use ApplicationCredential instead of Password
   # ── Step 1: File picker UI ────────────────────────────────────────────────
   root = tk.Tk()
   root.withdraw()  # Hide main window

   sa_key_path = filedialog.askopenfilename(
    title="Select Service Account Key JSON",
    filetypes=[("JSON files", "*.json")],
   )

   if not sa_key_path:
    raise ValueError("No file selected")

   # ── Step 2: Build STACKIT SDK client ─────────────────────────────────────
   stackit_config = Configuration(
    service_account_key_path=sa_key_path,
    custom_endpoint='https://iaas.api.eu01.stackit.cloud',
   )

   client = DefaultApi(stackit_config)
   project_id = config.STACKIT_PROJECT_ID

    
   
    # ── Step 3: Find the server by name ──────────────────────────────────────
    servers_response = client.list_servers(project_id=project_id)
    servers = [
        s for s in (servers_response.items or [])
        if s.name and s.name.lower() == vm_name
    ]
    if not servers:
        raise IndexError(f"VM '{vm_name}' not found in project {project_id}")

    server      = servers[0]
    server_id   = server.id
    boot_vol_id = server.boot_volume.id if server.boot_volume else None

    if not boot_vol_id:
        raise ValueError(f"Server '{vm_name}' has no boot volume attached.")

    # ── Step 4: Create a volume snapshot of the boot volume ──────────────────
    iaas_base   = getattr(config, 'STACKIT_IAAS_ENDPOINT',
                          'https://iaas.api.eu01.stackit.cloud')
    token       = stackit_config.get_access_token()        # SDK helper
    headers_json = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }

    snapshot_name = f"{vm_name}_snap_{int(time.time())}"
    snap_resp = requests.post(
        f"{iaas_base}/v1/projects/{project_id}/snapshots",
        headers=headers_json,
        json={"name": snapshot_name, "volumeId": boot_vol_id},
        timeout=30,
    )
    snap_resp.raise_for_status()
    snapshot_id = snap_resp.json()['id']

    # ── Step 5: Poll until snapshot is AVAILABLE ──────────────────────────────
    for _ in range(360):          # up to 2 hours (360 × 20 s)
        poll = requests.get(
            f"{iaas_base}/v1/projects/{project_id}/snapshots/{snapshot_id}",
            headers={'Authorization': f'Bearer {token}'},
            timeout=30,
        )
        poll.raise_for_status()
        status = poll.json().get('status', '')
        if status == 'AVAILABLE':
            break
        elif status == 'ERROR':
            raise RuntimeError(f"Snapshot {snapshot_id} entered ERROR state.")
        time.sleep(20)
    else:
        raise TimeoutError("Snapshot did not become AVAILABLE within 2 hours.")

    # ── Step 6: Create a local image/export from the snapshot ────────────────
    # STACKIT IaaS API: create a new volume from the snapshot, then export it.
    # (STACKIT does not currently offer a direct image-export endpoint; the
    #  recommended path is snapshot → new volume → download via backup/export.)
    #
    # If your STACKIT project has the "image export" feature enabled you can
    # alternatively POST to /v1/projects/{id}/images with source type "snapshot".

    image_name = f"{vm_name}_image_{int(time.time())}"
    img_resp = requests.post(
        f"{iaas_base}/v1/projects/{project_id}/images",
        headers=headers_json,
        json={
            "name":   image_name,
            "source": {"id": snapshot_id, "type": "snapshot"},
        },
        timeout=30,
    )
    img_resp.raise_for_status()
    image_id = img_resp.json()['id']

    # ── Step 7: Poll until image is AVAILABLE ─────────────────────────────────
    for _ in range(360):
        poll = requests.get(
            f"{iaas_base}/v1/projects/{project_id}/images/{image_id}",
            headers={'Authorization': f'Bearer {token}'},
            timeout=30,
        )
        poll.raise_for_status()
        status = poll.json().get('status', '')
        if status == 'AVAILABLE':
            break
        elif status == 'ERROR':
            raise RuntimeError(f"Image {image_id} entered ERROR state.")
        time.sleep(20)
    else:
        raise TimeoutError("Image did not become AVAILABLE within 2 hours.")

    # ── Step 8: Download the image with resume / retry ────────────────────────
    download_url = f"{iaas_base}/v1/projects/{project_id}/images/{image_id}/file"

    for attempt in range(5):
        try:
            resume_pos = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            dl_headers = {'Authorization': f'Bearer {token}'}
            if resume_pos > 0:
                dl_headers['Range'] = f'bytes={resume_pos}-'

            response = requests.get(download_url, headers=dl_headers,
                                    stream=True, timeout=30)
            response.raise_for_status()

            mode = 'ab' if resume_pos > 0 else 'wb'
            with open(output_path, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)

            return {
                'message':     (f"Image '{image_name}' (ID: {image_id}) "
                                f"downloaded to {output_path}"),
                'output_path': output_path,
            }

        except (requests.exceptions.RequestException, IOError) as e:
            if attempt < 4:
                time.sleep(2 ** attempt)   # exponential back-off
                continue
            return False, f"Download failed after 5 attempts: {e}"

       
   



#except (requests.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
#                       #print(f"\nConnection error, retrying... ({e})")
#                       sleep(5)  # wait a few seconds
#                       max_retries -= 1
#                       if max_retries <= 0:
#                           raise Exception("Max retries exceeded")down
