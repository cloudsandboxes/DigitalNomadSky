#!/usr/bin/env python3
"""
T Cloud Public (T-Systems) OpenStack VM Access Script
This script authenticates to T Cloud Public OpenStack
"""
def fetch_vm(vmname):
    import os
    import sys
    import requests
    import json
    import tkinter as tk
    from tkinter import filedialog

    sys.path.append(r"C:/projects/digitalnomadsky/code/T-systems")
    import config

    source = sys.argv[1]
    destination = sys.argv[2]
    vm_name = sys.argv[3].lower()

    sourcelocation = source  # e.g. 'eu-nl'
    sourcecloudurl = f"https://iam.{sourcelocation}.otc.t-systems.com:443/v3"

    # ── Step 1: File picker for clouds.yaml or JSON credentials ──────────────
    root = tk.Tk()
    root.withdraw()
    creds_path = filedialog.askopenfilename(
        title="Select credentials JSON file",
        filetypes=[("JSON files", "*.json")],
    )
    if not creds_path:
        raise ValueError("No file selected")

    with open(creds_path) as f:
        creds = json.load(f)

    username        = creds["username"]
    password        = creds["password"]
    project_name    = creds["project_name"]
    user_domain_name = creds["user_domain_name"]

    # ── Step 2: Authenticate and get token ───────────────────────────────────
    auth_payload = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": username,
                        "password": password,
                        "domain": {"name": user_domain_name}
                    }
                }
            },
            "scope": {
                "project": {"name": project_name}
            }
        }
    }

    auth_response = requests.post(
        f"{sourcecloudurl}/auth/tokens",
        json=auth_payload
    )
    auth_response.raise_for_status()
    token = auth_response.headers["X-Subject-Token"]

    # Get compute endpoint from service catalog
    catalog = auth_response.json()["token"]["catalog"]
    compute_endpoint = next(
        e["url"]
        for svc in catalog if svc["type"] == "compute"
        for e in svc["endpoints"] if e["interface"] == "public"
    )

    # ── Step 3: Find server by name ──────────────────────────────────────────
    headers = {"X-Auth-Token": token}
    servers_response = requests.get(
        f"{compute_endpoint}/servers/detail",
        headers=headers
    )
    servers_response.raise_for_status()

    servers = [
        s for s in servers_response.json().get("servers", [])
        if s.get("name", "").lower() == vm_name
    ]

    if not servers:
        raise IndexError(f"VM '{vm_name}' not found in project {project_name}")

    server = servers[0]
    boot_vol_id = next(
        (v["id"] for v in server.get("os-extended-volumes:volumes_attached", [])),
        None
    )
    if not boot_vol_id:
        raise ValueError(f"Server '{vm_name}' has no boot volume attached.")

    result = {
        'message': f"VM '{vm_name}' found successfully in {source}!",
        'id': server["id"],
        'vm_name': server["name"],
        'status': server["status"],
        'flavor': server.get("flavor"),
        'networks': server.get("addresses"),
    }

    return result
