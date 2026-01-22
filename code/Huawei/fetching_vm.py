"""
Huawei Cloud VM Management Script

Required pip packages:
py -m pip install huaweicloudsdkcore
py -m pip install huaweicloudsdkecs
py -m pip install huaweicloudsdkims
py -m pip install huaweicloudsdkevs
py -m pip install huaweicloudsdkobs

Required config.py files:
1. C:/projects/nomadsky/code/huawei/config.py with:
   vm_name = "your-vm-name"
   ak = "your-access-key"
   sk = "your-secret-key"
   project_id = "your-project-id"
   region = "eu-west-0"
   obs_bucket = "vm-export-bucket"
   download_path = "C:/temp"

Note: Huawei Cloud supports QCOW2, VMDK, VHD, and ZVHD2 formats for export.
QCOW2 is recommended as it's native to Huawei Cloud.
"""
def search_huawei_vm():

    import sys
    import os
    import time
    from datetime import datetime

    # Huawei Cloud imports
    from huaweicloudsdkcore.auth.credentials import BasicCredentials
    from huaweicloudsdkcore.http.http_config import HttpConfig
    from huaweicloudsdkecs.v2 import EcsClient, ListServersDetailsRequest
    from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
    from huaweicloudsdkims.v2 import ImsClient, CreateWholeImageRequest, CreateWholeImageRequestBody
    from huaweicloudsdkims.v2.region.ims_region import ImsRegion
    from huaweicloudsdkevs.v2 import EvsClient, ListVolumesRequest
    from huaweicloudsdkevs.v2.region.evs_region import EvsRegion
    from huaweicloudsdkobs import ObsClient

    sys.path.append(r"C:/projects/nomadsky/code/huawei")
    import config
    source = sys.argv[1]
    destination = sys.argv[2]
    vm_name = sys.argv[3].lower()

    """
    Search for a VM in Huawei Cloud by name.
    
    Returns:
        dict: VM details including id, size, os, and disk information
    
    Raises:
        Exception: If VM not found
    """
    
    # Get parameters from config
    ak = config.ak
    sk = config.sk
    region = config.region
    project_id = config.project_id
    
    print(f"Searching for VM '{vm_name}' in Huawei Cloud...")
    
    # Interactive login
    credentials = BasicCredentials(ak, sk, project_id)
    
    # Create ECS client
    ecs_client = EcsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(EcsRegion.value_of(region)) \
        .build()
    
    # Create EVS client for disk details
    evs_client = EvsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(EvsRegion.value_of(region)) \
        .build()
    
    try:
        # Search for server by name
        request = ListServersDetailsRequest()
        request.name = vm_name
        
        response = ecs_client.list_servers_details(request)
        
        if not response.servers or len(response.servers) == 0:
            raise Exception(f"VM '{vm_name}' not found in Huawei Cloud")
        
        server = response.servers[0]
        
        # Extract server details
        server_id = server.id
        server_name = server.name
        flavor_name = server.flavor.name
        status = server.status
        
        # Determine OS type
        os_type = "Linux"
        if server.metadata and 'os_type' in server.metadata:
            os_type = server.metadata['os_type']
        elif server.image and 'os_type' in server.image:
            os_type = server.image.get('os_type', 'Linux')
        
        # Get disk details
        disks = []
        if server.os_ext_vol_attached_volumes:
            for vol in server.os_ext_vol_attached_volumes:
                volume_id = vol.id
                
                # Get volume details
                vol_request = ListVolumesRequest()
                vol_request.volume_id = volume_id
                vol_response = evs_client.list_volumes(vol_request)
                
                if vol_response.volumes and len(vol_response.volumes) > 0:
                    volume = vol_response.volumes[0]
                    disk_info = {
                        'volume_id': volume_id,
                        'device': vol.device if hasattr(vol, 'device') else 'N/A',
                        'size_gb': volume.size,
                        'volume_type': volume.volume_type,
                        'bootable': volume.bootable == 'true'
                    }
                    disks.append(disk_info)
        
        result = {
            'message': f"VM '{vm_name}' found successfully in Huawei Cloud!",
            'source': 'Huawei Cloud',
            'vm_name': server_name,
            'server_id': server_id,
            'vm_size': flavor_name,
            'status': status,
            'os_type': os_type,
            'resource_id': server_id,
            'region': region,
            'disk_details': disks
        }
        
        print(f"VM found: {server_id}")
        return result
        
    except Exception as e:
        raise Exception(f"Failed to search for VM '{vm_name}': {str(e)}")
