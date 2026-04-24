#!/usr/bin/env python3
def stop_vm():    
    """
    Stackit.cloud OpenStack VM Access Script
    This script authenticates to Stackit.cloud OpenStack
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

    # ── Suspend VM ───────────────────────────────────────────────────────────
    if server.status != "SUSPENDED":
     client.suspend_server(
        project_id=project_id,
        server_id=server.id
     )

     # ── Wait for state change ────────────────────────────────────────────
     for _ in range(30):
        updated = client.get_server(
            project_id=project_id,
            server_id=server.id
        )

        if updated.status == "SUSPENDED":
            return {"message": f"VM {vm_name} suspended"}

        time.sleep(5)

     raise TimeoutError(f"Timeout while suspending VM '{vm_name}'")

    else:
     return {"message": f"VM {vm_name} is already suspended"}

