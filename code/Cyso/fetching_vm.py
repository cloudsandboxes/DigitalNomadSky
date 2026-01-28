#!/usr/bin/env python3
"""
Cyso.cloud OpenStack VM Access Script
This script authenticates to Cyso.cloud OpenStack and provides VNC console access to VMs
"""

def fetch_vm (vmname):
   """
   Get OpenStack credentials from environment variables or user input.
   You can download your OpenStack RC file from Cyso.cloud dashboard.
   https://core.fuga.cloud:5000/v3
   https://identity.api.ams.fuga.cloud:443/v3
   """
   import os
   import sys
   import webbrowser
   from novaclient import client as nova_client
   from keystoneauth1 import session
   from keystoneauth1.identity import v3
   import getpass
   import json
   sys.path.append(r"C:/projects/nomadsky/code/Cyso")
   import tkinter as tk
   from tkinter import simpledialog


   # Get arguments
   source = sys.argv[1]
   destination = sys.argv[2]
   vm_name = sys.argv[3].lower()
   import config
   
   # Step 1: Get credentials
   print("\n[1/4] Getting credentials...")
   # Use ApplicationCredential instead of Password
   from keystoneauth1.identity.v3 import ApplicationCredential

   root = tk.Tk()
   root.title("Application secret required")
   root.geometry("300x120")
   tk.Label(root, text="Enter secret:").pack(pady=10)
   password_var = tk.StringVar()
   done_var = tk.BooleanVar(value=False)

   password_entry = tk.Entry(root, show="*", textvariable=password_var)
   password_entry.pack()

   tk.Button(
     root,
     text="OK",
     command=lambda: done_var.set(True)
   ).pack(pady=10)

   
   # Wait until the button is pressed
   root.wait_variable(done_var)

   password = password_var.get()
   root.destroy()

   
   auth = ApplicationCredential(
    auth_url=os.environ.get('OS_AUTH_URL', 'https://core.fuga.cloud:5000/v3'),
    application_credential_id=config.OS_APPLICATION_CREDENTIAL_ID,
    application_credential_secret= password
   )
   sess = session.Session(auth=auth)
   nova = nova_client.Client("2.1", session=sess)
    
   #servers = nova.servers.list()
   servers = nova.servers.list(search_opts={'name': vm_name})
    
   if not servers:
        return None
    
   # Return first match (names can be duplicate)
   server = servers[0]
    
   # Get all properties
   result = {
        'message': f"VM '{vm_name}' found successfully in {source}!",
        'vmname' : vm_name,
        'whatups': vm_name
            }
   #'networks': server.networks
   #'created': server.created
   #'flavor': server.flavor,
   #'image': server.image
   #        'id': server.id,
   #     'name': server.name,
   #    'status': server.status

   return result 

