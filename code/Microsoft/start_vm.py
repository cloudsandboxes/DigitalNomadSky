def start_vm ():
  import sys
  from azure.identity import DefaultAzureCredential
  from azure.mgmt.compute import ComputeManagementClient
  from azure.mgmt.network import NetworkManagementClient
  from azure.mgmt.resource import ResourceManagementClient
  import tkinter as tk
  from tkinter import simpledialog

  root = tk.Tk()
  root.withdraw()  # hide main window

  username = simpledialog.askstring("Credentials", "Enter username:")
  password = simpledialog.askstring("Credentials", "Enter password:", show="*")

  #print(f"Username: {username}, Password: {password}")

  subscription_id = "YOUR_SUBSCRIPTION_ID"
  resource_group = "YOUR_RESOURCE_GROUP"
  vm_name = "MyVM"
  location = "eastus"
  vhd_url = "https://<storage_account>.blob.core.windows.net/<container>/<vhd_file>.vhd"

  credential = DefaultAzureCredential()
  compute_client = ComputeManagementClient(credential, subscription_id)
  network_client = NetworkManagementClient(credential, subscription_id)
  resource_client = ResourceManagementClient(credential, subscription_id)

  # --- Example: assume a network interface already exists ---
  nic_id = "/subscriptions/.../resourceGroups/.../providers/Microsoft.Network/networkInterfaces/MyNIC"

  vm_params = {
      "location": location,
      "hardware_profile": {
          "vm_size": "Standard_DS1_v2"
      },
      "storage_profile": {
          "os_disk": {
              "os_type": "Linux",  # or "Windows"
              "name": f"{vm_name}_OSDisk",
              "caching": "ReadWrite",
              "create_option": "FromImage",
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
          "admin_username": "azureuser",
          "admin_password": "YourPassword123!"  # for Windows/Linux
      }
  }

  async_vm_creation = compute_client.virtual_machines.begin_create_or_update(resource_group, vm_name, vm_params)
  async_vm_creation.wait()
  print(f"VM {vm_name} created from VHD!")
