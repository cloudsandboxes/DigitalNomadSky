#!/usr/bin/env python3
"""
Cyso.cloud OpenStack VM Access Script
This script authenticates to Cyso.cloud OpenStack and provides VNC console access to VMs
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
#source = sys.argv[1]
#destination = sys.argv[2]
#vmname = sys.argv[3].lower()
import config
vm_name='ubuntu'
def fetch_vm ():
   """
   Get OpenStack credentials from environment variables or user input.
   You can download your OpenStack RC file from Cyso.cloud dashboard.
   https://core.fuga.cloud:5000/v3
   https://identity.api.ams.fuga.cloud:443/v3
   """
   # Step 1: Get credentials
   print("\n[1/4] Getting credentials...")
   # Use ApplicationCredential instead of Password
   from keystoneauth1.identity.v3 import ApplicationCredential

   root = tk.Tk()
   root.title("Password required")
   root.geometry("300x120")

   tk.Label(root, text="Enter password:").pack(pady=10)

   password_entry = tk.Entry(root, show="*")
   password_entry.pack()

   def on_submit():
    password = password_entry.get()
    print("Password entered (not shown for security reasons)")
    root.destroy()

   tk.Button(root, text="OK", command=on_submit).pack(pady=10)

   root.mainloop()

    
   auth = ApplicationCredential(
    auth_url=os.environ.get('OS_AUTH_URL', 'https://core.fuga.cloud:5000/v3'),
    application_credential_id=config.OS_APPLICATION_CREDENTIAL_ID,
    application_credential_secret=os.environ.get('OS_APPLICATION_CREDENTIAL_SECRET') or getpass.getpass("Enter your app credential secret: ")
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
   return {
        'id': server.id,
        'name': server.name,
        'status': server.status,
        'flavor': server.flavor,
        'image': server.image,
        'networks': server.networks,
        'created': server.created,
    }

try:
     number = fetch_vm()
     print("✓ Authentication successful!")
     print (f"Success! Found {number} VMs")
except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\nPlease check your credentials and try again.")
        sys.exit(1)
