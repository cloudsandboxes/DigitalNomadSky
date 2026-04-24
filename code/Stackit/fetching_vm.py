#!/usr/bin/env python3
"""
Stackit.cloud OpenStack VM Access Script
This script authenticates to stackit.cloud OpenStack
"""

def fetch_vm (vmname):
   """
   Get OpenStack credentials from environment variables or user input.
   You can download your OpenStack RC file from stackit.cloud dashboard.
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
   boot_vol_id = server.boot_volume.id if server.boot_volume else None

   if not boot_vol_id:
       raise ValueError(f"Server '{vm_name}' has no boot volume attached.") 
   # Get all properties
   result = {
        'message': f"VM '{vm_name}' found successfully in {source}!",
        'id': server.id,
        'vm_name': server.name,
        'status': server.status,
        'flavor': server.flavor,
        'networks': server.networks
            }
   #'created': server.created
   #'image': server.image
   
   return result 
