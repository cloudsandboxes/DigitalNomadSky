def start_vm (shared_data):
  import sys
  sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
  from azure.identity import InteractiveBrowserCredential
  from azure.mgmt.compute import ComputeManagementClient
  from azure.mgmt.network import NetworkManagementClient
  from azure.mgmt.resource import ResourceManagementClient
  import config
  import re
  
  subscription_id = config.subscription_id
  resource_group = config.resource_group
  vm_name = shared_data.get('vm_name', '')
  location = config.location
  account_url = shared_data.get('disk_url', '')
  vhd_url = account_url + "/" + config.container_name + "/" + config.blob_name
  nic_id = shared_data.get('nic_id', '')
  os_type = shared_data.get('os_type', '')
  vm_size = shared_data.get('vm_size', '')

  

  #vhd_url = 'https://compliceert20.blob.core.windows.net/vhds/osdisk.vhd'
  
  tenant_id = config.destionationtenantid
  credential = InteractiveBrowserCredential(tenant_id=tenant_id)
  compute_client = ComputeManagementClient(credential, subscription_id)
  network_client = NetworkManagementClient(credential, subscription_id)
  resource_client = ResourceManagementClient(credential, subscription_id)

  disk_params = {
    "location": location,
    "creation_data": {
        "create_option": "Import",
        "source_uri": vhd_url
    },
    "sku": {"name": "Standard_LRS"}  # optional: Standard HDD/SSD
  }

  managed_disk = compute_client.disks.begin_create_or_update(
    resource_group_name,
    "MyManagedDisk",
    disk_params
  ).result()
 
  vm_params = {
      "location": location,
      "hardware_profile": {
          "vm_size": vm_size
      },
      "storage_profile": {
          "os_disk": {
              "os_type": "Windows", # os_type   "Windows" or "Linux"
              "name": f"{vm_name}_OSDisk",
              "caching": "ReadWrite",
              "create_option": "Attach",
              "managed_disk": {"id": managed_disk.id},
          }
      },
      "network_profile": {
          "network_interfaces": [
              {"id": nic_id, "primary": True}
          ]
      }      
  }
  
  async_vm_creation = compute_client.virtual_machines.begin_create_or_update(resource_group, vm_name, vm_params)
  async_vm_creation.wait()
  #print(f"VM {vm_name} created from VHD!")
