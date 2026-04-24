#!/usr/bin/env python3
def uploading_disk(vm_name):
    """
    Stackit.cloud OpenStack VM Access Script
    This script authenticates to Stackit.cloud OpenStack and uploads the image
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
    
    shared_data = json.loads(sys.argv[4])
    disktype = shared_data.get("importdisktype", "")
    output_path = shared_data.get("output_path", "")

     
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
    
    
    image_name= f"osdisk-{vm_name}"
    disk_format=disktype
    if source == "azure":
        disk_format="raw"
 
    # ── Create image in STACKIT ─────────────────────────────────────────────
    image = client.create_image(
        project_id=project_id,
        body={
            "name": image_name,
            "diskFormat": disk_format,
            "containerFormat": "bare",
            "visibility": "private",
        },
    )

    image_id = image.id

    # ── Trigger upload/import (STACKIT-managed) ─────────────────────────────
    with open(output_path, "rb") as f:
        client.upload_image(
            project_id=project_id,
            image_id=image_id,
            body=f,
        )

    # ── Wait for ACTIVE state ───────────────────────────────────────────────
    for _ in range(360):  # ~30 minutes
        img = client.get_image(
            project_id=project_id,
            image_id=image_id,
        )

        if img.status == "ACTIVE":
            return {
                "message": f"Image {image_name} uploaded successfully",
                "image_id": image_id,
            }

        if img.status == "ERROR":
            raise RuntimeError(
                f"Image upload failed for {image_name} in {destination}"
            )

        time.sleep(5)

    raise TimeoutError(
        f"Image upload timeout for {image_name} in {destination}"
    )
