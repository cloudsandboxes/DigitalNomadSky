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
