#!/usr/bin/env python3
def create_vm_from_image(shared_data):
    """
    leaf.cloud OpenStack VM Access Script
    This script authenticates to leaf.cloud OpenStack and starts the image
    """
    import os
    import sys
    import webbrowser
    from novaclient import client as nova_client
    from glanceclient import client as glance_client
    #from neutronclient import client as neutron_client
    from keystoneauth1 import session
    from keystoneauth1.identity import v3
    import json
    sys.path.append(r"C:/projects/nomadsky/code/LeafCloud")
    import tkinter as tk
    from tkinter import simpledialog
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
     auth_url=os.environ.get('OS_AUTH_URL', config.destinationcloudurl),
     application_credential_id=config.OS_APPLICATION_CREDENTIAL_ID,
     application_credential_secret= password
    )
    sess = session.Session(auth=auth)
    nova = nova_client.Client("2.1", session=sess)
        
    # Create server
    server = nova.servers.create(
        name=vm_name,
        image=image_id,
        flavor="3bc4833f-dc05-4633-a6b1-8c764c4ce857",
        nics=config.nics
    )
    
    # Wait for VM to become active (check every 5 seconds, max 10 minutes)
    for _ in range(120):
        srv = nova.servers.get(server.id)
        if srv.status == 'ACTIVE':
            return {'message': f"VM {vm_name} created (ID: {server.id})"}
        elif srv.status == 'ERROR':
            raise IndexError(f"VM '{vmname}' creation timeout in {destination}")
        time.sleep(20)
    
    raise IndexError(f"VM '{vmname}' cration timeout in {destination}") 
