
#!/usr/bin/env python3
def export_os_disk(vm_name):
    """
    Cyso.cloud OpenStack VM Access Script
    This script authenticates to Cyso.cloud OpenStack and downloads the image
    """
    
    import os
    import sys
    import webbrowser
    from novaclient import client as nova_client
    from glanceclient import client
    from keystoneauth1 import session
    from keystoneauth1.identity import v3
    import getpass
    import json
    sys.path.append(r"C:/projects/nomadsky/code/Cyso")
    import tkinter as tk
    from tkinter import simpledialog
    import time

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
     auth_url=os.environ.get('OS_AUTH_URL', 'https://core.fuga.cloud:5000/v3'),
     application_credential_id=config.OS_APPLICATION_CREDENTIAL_ID,
     application_credential_secret= password
    )
    sess = session.Session(auth=auth)
    nova = nova_client.Client("2.1", session=sess)
    
    # Find VM by name
    servers = nova.servers.list(search_opts={'name': vm_name})
    if not servers:
        return False, "VM not found"
    
    server = servers[0]
    
    # Create snapshot/image of the VM
    image_name = f"{vm_name}_snapshot_{int(__import__('time').time())}"
    image_id = server.create_image(image_name)
    for _ in range(360):
        image = glance.images.get(image_id)
        if image.status == 'active':
            return {'message': f"Image {image_name} ready (ID: {image_id})"}
        elif image.status == 'error':
            return False, f"Image creation failed"
        time.sleep(20)

""""
    
def download_image(image_id, output_path, disk_format='qcow2', chunk_size=8192):
    from keystoneauth1 import session
    from keystoneauth1.identity.v3 import ApplicationCredential
    from glanceclient import Client
    import requests
    import os
    import time
    
    # Auth setup
    auth = ApplicationCredential(
        auth_url=os.environ.get('OS_AUTH_URL', 'https://core.fuga.cloud:5000/v3'),
        application_credential_id=os.environ.get('OS_APPLICATION_CREDENTIAL_ID'),
        application_credential_secret=os.environ.get('OS_APPLICATION_CREDENTIAL_SECRET')
    )
    sess = session.Session(auth=auth)
    glance = Client('2', session=sess)
    
    # Get image download URL
    image = glance.images.get(image_id)
    download_url = glance.images.data(image_id, do_checksum=False)
    
    # Get direct URL from Glance endpoint
    endpoint = sess.get_endpoint(service_type='image')
    url = f"{endpoint}/v2/images/{image_id}/file"
    
    # Download with retry (max 5 attempts)
    for attempt in range(5):
        try:
            # Resume from where we left off
            resume_pos = os.path.getsize(output_path) if os.path.exists(output_path) else 0
            headers = {'Range': f'bytes={resume_pos}-'} if resume_pos > 0 else {}
            headers['X-Auth-Token'] = sess.get_token()
            
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            
            mode = 'ab' if resume_pos > 0 else 'wb'
            with open(output_path, mode) as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
            
            return True, f"Downloaded to {output_path}"
            
        except (requests.exceptions.RequestException, IOError) as e:
            if attempt < 4:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            return False, f"Download failed after 5 attempts: {e}"
"""
