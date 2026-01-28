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

def fetch_vm ():
   """
   Get OpenStack credentials from environment variables or user input.
   You can download your OpenStack RC file from Cyso.cloud dashboard.
   https://core.fuga.cloud:5000/v3
   https://identity.api.ams.fuga.cloud:443/v3
   """
   # Step 1: Get credentials
   print("\n[1/4] Getting credentials...")
   # For app credentials, only need ID and secret
   creds = {
        'auth_url': os.environ.get('OS_AUTH_URL', 'https://core.fuga.cloud:5000/v3'),
        'application_credential_id': os.environ.get('OS_APPLICATION_CREDENTIAL_ID', '33730d2e61274dd584f0d7b2fa846fba'),
        'application_credential_secret': os.environ.get('OS_APPLICATION_CREDENTIAL_SECRET') or getpass.getpass("Enter your app credntial secret: "),
    }

   # Use ApplicationCredential instead of Password
   from keystoneauth1.identity.v3 import ApplicationCredential
    
   auth = ApplicationCredential(
        auth_url=creds['auth_url'],
        application_credential_id=creds['application_credential_id'],
        application_credential_secret=creds['application_credential_secret']
    )
   sess = session.Session(auth=auth)
   nova = nova_client.Client("2.1", session=sess)
    
   servers = nova.servers.list()
   return nova, len(servers)


try:
     nova, number = fetch_vm()
     servers = nova.servers.list()
     print("✓ Authentication successful!")
     print (f"Success! Found {len(servers)}, {number} VMs")
except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\nPlease check your credentials and try again.")
        sys.exit(1)
