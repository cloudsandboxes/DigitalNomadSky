def start_vm (shared_data):
  import sys
  sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
  from azure.identity import InteractivebrowserCredential
  from azure.mgmt.compute import ComputeManagementClient
  from azure.mgmt.network import NetworkManagementClient
  from azure.mgmt.resource import ResourceManagementClient
  import tkinter as tk
  from tkinter import simpledialog, messagebox
  import config
  import re

  root = tk.Tk()
  root.withdraw()  # hide main window

  username = simpledialog.askstring("Credentials", "Enter username:")
  
  while True:
      password = simpledialog.askstring("Password", "Enter a password:", show="*")
      if password is None:  # user cancelled
          break

      # Check rules: min 15 chars, at least 1 uppercase, 1 number, 1 special
      if (len(password) >= 15 and
          re.search(r"[A-Z]", password) and
          re.search(r"[0-9]", password) and
          re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
          messagebox.showinfo("Success", "Password accepted!")
          break
      else:
          messagebox.showerror("Invalid", "Password must be at least 15 characters with uppercase, number, and special character.")
  

  #print(f"Username: {username}, Password: {password}")

  subscription_id = config.subscritpion_id
  resource_group = config.resource_group
  vm_name = shared_data.get('vm_name', '')
  location = config.location
  account_url = shared_data.get('account_url', '')
  vhd_url = account_url + "/" + config.container_name + "/" + config.blob_name
  nic_id = shared_data.get('nic_id', '')
  os_type = shared_data.get('os_type', '')
  vm_size = shared_data.get('vm_size', '')
  
  credential = InteractiveBrowserCredential()
  compute_client = ComputeManagementClient(credential, subscription_id)
  network_client = NetworkManagementClient(credential, subscription_id)
  resource_client = ResourceManagementClient(credential, subscription_id)

  vm_params = {
      "location": location,
      "hardware_profile": {
          "vm_size": vm_size
      },
      "storage_profile": {
          "os_disk": {
              "os_type": os_type  # "Windows" or "Linux"
              "name": f"{vm_name}_OSDisk",
              "caching": "ReadWrite",
              "create_option": "FromImage",
              "managed_disk": {"storage_account_type": "Standard_LRS"  # options: Standard_LRS, StandardSSD_LRS, Premium_LRS},
              "vhd": {
                  "uri": vhd_url
              }
          }
      },
      "network_profile": {
          "network_interfaces": [
              {"id": nic_id, "primary": True}
          ]
      },
      "os_profile": {
          "computer_name": vm_name,
          "admin_username": username,
          "admin_password": password  # for Windows/Linux
      }
  }

  async_vm_creation = compute_client.virtual_machines.begin_create_or_update(resource_group, vm_name, vm_params)
  async_vm_creation.wait()
  #print(f"VM {vm_name} created from VHD!")
