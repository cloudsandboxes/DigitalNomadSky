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

"""
Get OpenStack credentials from environment variables or user input.
You can download your OpenStack RC file from Cyso.cloud dashboard.
"""
credentials = {
        'auth_url': os.environ.get('OS_AUTH_URL', 'https://identity.api.ams.fuga.cloud:443/v3'),
        'username': os.environ.get('OS_USERNAME'),
        'password': os.environ.get('OS_PASSWORD'),
        'project_name': os.environ.get('OS_PROJECT_NAME'),
        'user_domain_name': os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
        'project_domain_name': os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default'),
    }
    
# Prompt for missing credentials
if not credentials['username']:
      credentials['username'] = input("Enter your OpenStack username: ")
if not credentials['password']:
      import getpass
      credentials['password'] = getpass.getpass("Enter your OpenStack password: ")
if not credentials['project_name']:
     credentials['project_name'] = input("Enter your project name: ")
    
"""
Create an authenticated Nova client using Keystone v3 authentication.
"""
auth = v3.Password(
        auth_url=credentials['auth_url'],
        username=credentials['username'],
        password=credentials['password'],
        project_name=credentials['project_name'],
        user_domain_name=credentials['user_domain_name'],
        project_domain_name=credentials['project_domain_name']
    )
    
sess = session.Session(auth=auth)
nova = nova_client.Client("2.1", session=sess)
print(nova)    

