#!/usr/bin/env python3
def create_vm_from_image(shared_data):
    """
    stackit.cloud OpenStack VM Access Script
    This script authenticates to stackit.cloud OpenStack and starts the image
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
    vmname=f"{vm_name}-new"
    import config
    shared_data_json = sys.argv[4]  # 4th argument
    shared_data = json.loads(shared_data_json)
    # Extract specific value
    image_id = shared_data.get('image_id', '')
     
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
    
        
    server = client.create_server(
        project_id=project_id,
        body={
            "name": vmname,
            "imageId": image_id,
            "flavor": "cc1.xsmall",
            "networks": config.nics,
        },
    )

    server_id = server.id

    # ── Wait for ACTIVE state ───────────────────────────────────────────────
    for _ in range(120):  # ~10 minutes
        srv = client.get_server(
            project_id=project_id,
            server_id=server_id,
        )

        if srv.status == "ACTIVE":
            return {
                "message": f"VM {vmname} created successfully",
                "server_id": server_id,
            }

        if srv.status == "ERROR":
            raise RuntimeError(
                f"VM creation failed for {vmname} in {destination}"
            )

        time.sleep(5)

    raise TimeoutError(
        f"VM creation timeout for {vmname} in {destination}"
    )
