#!/usr/bin/env python3
def uploading_disk(vm_name):
    """
    Cyso.cloud OpenStack VM Access Script
    This script authenticates to Cyso.cloud OpenStack and downloads the image
    """
    
    import os
    import sys
    import webbrowser
    from novaclient import client as nova_client
    from glanceclient import client as glance_client
    from keystoneauth1 import session
    from keystoneauth1.identity import v3
    import getpass
    import json
    sys.path.append(r"C:/projects/nomadsky/code/Cyso")
    import tkinter as tk
    from tkinter import simpledialog
    import time
    import requests
    from requests.exceptions import ConnectionError, ChunkedEncodingError
    

    # Get arguments
    source = sys.argv[1]
    destination = sys.argv[2]
    vm_name = sys.argv[3].lower()
    import config
    
    chunk_size = 50 * 1024 * 1024  # 50 MB per chunk
    shared_data_json = sys.argv[4]  # 4th argument
    shared_data = json.loads(shared_data_json)
    # Extract specific value
    disktype = shared_data.get('importdisktype', '')
    output_path = shared_data.get('output_path', '')
    


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
    glance = glance_client.Client("2", session=sess)

    image_name= f"osdisk-{vm_name}"
    disk_format=disktype
    container_format='bare'
    if source == "azure":
        disk_format="raw"
 
    # Create image metadata
    image = glance.images.create(
        name=image_name,
        disk_format=disk_format,
        container_format=container_format,
        visibility='private'
    )

    
    # Upload in chunks
    chunk_size = 8192
    file_size = os.path.getsize(output_path)
    uploaded = 0
   
    with open(output_path, 'rb') as f:
        glance.images.upload(image.id, f)
    
    # Wait for image to become active (check every 5 seconds, max 30 minutes)
    for _ in range(360):
        img = glance.images.get(image.id)
        if img.status == 'active':
            return {'message' : f"Image {image_name} uploaded (ID: {image.id})",
                   'image_id' : image.id}
        elif img.status == 'error':
            return False, f"Upload failed"
        time.sleep(20)
    
    return False, f"Upload timeout"
