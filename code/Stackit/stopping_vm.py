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
     auth_url=os.environ.get('OS_AUTH_URL', config.sourcecloudurl),
     application_credential_id=config.OS_APPLICATION_CREDENTIAL_ID,
     application_credential_secret= password
    )
    sess = session.Session(auth=auth)
    nova = nova_client.Client("2.1", session=sess)

    # Find VM by name
    servers = nova.servers.list(search_opts={'name': vm_name})
    if not servers:
        raise IndexError(f"VM '{vmname}' not found in {source}")
    
    server = servers[0]
    if server.status != "SUSPENDED":
        server.suspend()  # Graceful shutdown
        for _ in range(30):
            server = nova.servers.get(server.id)
            if server.status == 'SUSPENDED':
                return {'message' : f"VM {vm_name} stopped"}
            time.sleep(15)
    else:         
        return {'message' : f"VM {vm_name} was already stopped"}
