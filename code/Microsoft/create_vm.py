def start_vm (shared_data):
  import sys
  sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
  from azure.identity import InteractiveBrowserCredential
  from azure.mgmt.compute import ComputeManagementClient
  from azure.mgmt.network import NetworkManagementClient
  from azure.mgmt.resource import ResourceManagementClient
  from azure.mgmt.compute.models import Disk, CreationData, DiskCreateOption,
    VirtualMachine,
    HardwareProfile,
    StorageProfile,
    OSDisk,
    OSProfile,
    NetworkProfile,
    NetworkInterfaceReference,
    ManagedDiskParameters
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
  disk_name: "disk-name-mooi-{vm_name}",
  

  #vhd_url = 'https://compliceert20.blob.core.windows.net/vhds/osdisk.vhd'
  
  tenant_id = config.destionationtenantid
  credential = InteractiveBrowserCredential(tenant_id=tenant_id)
  compute_client = ComputeManagementClient(credential, subscription_id)
  network_client = NetworkManagementClient(credential, subscription_id)
  resource_client = ResourceManagementClient(credential, subscription_id)

  
  # Create managed disk from VHD
  disk_params = Disk(
      location=location,
      creation_data={
          'create_option': DiskCreateOption.IMPORT,
          'source_uri': vhd_url
        },
      os_type= "Windows"
    )
    
  disk_creation = compute_client.disks.begin_create_or_update(
        resource_group,
        disk_name,
        disk_params
    )

  disk_creation.wait()
  managed_disk = disk_creation.result()
  #print(f"Managed disk created: {managed_disk.id}")
  #print(f"Creating VM '{vm_name}'...")
    
  # Create VM from managed disk
  vm_params = VirtualMachine(
        location=location,
        hardware_profile=HardwareProfile(
            vm_size=vm_size
        ),
        storage_profile=StorageProfile(
            os_disk=OSDisk(
                os_type=os_type,
                create_option=DiskCreateOption.ATTACH,
                managed_disk=ManagedDiskParameters(
                    id=managed_disk.id
                )
            )
        ),
        network_profile=NetworkProfile(
            network_interfaces=[
                NetworkInterfaceReference(
                    id=nic_id,
                    primary=True
                )
            ]
        )
    )
    
  vm_creation = compute_client.virtual_machines.begin_create_or_update(
        resource_group,
        vm_name,
        vm_params
    )
  vm_creation.wait()
    
  vm = vm_creation.result()
  #print(f"VM created successfully: {vm.id}")
    
  return {
        'disk_id': managed_disk.id,
        'vm_id': vm.id,
        'vm_name': vm.name,
        'disk_name': managed_disk.name
    }
  
