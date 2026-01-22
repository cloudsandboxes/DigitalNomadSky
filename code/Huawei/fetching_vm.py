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


def search_huawei_vm():
    """
    Search for a VM in Huawei Cloud by name.
    
    Returns:
        dict: VM details including id, size, os, and disk information
    
    Raises:
        Exception: If VM not found
    """
    
    # Get parameters from config
    vm_name = config.vm_name
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


def stop_huawei_vm():
    """
    Stop a VM in Huawei Cloud.
    
    Returns:
        dict: Result with message about stop operation
    
    Raises:
        Exception: If VM not found or stop fails
    """
    
    # Get parameters from config
    vm_name = config.vm_name
    ak = config.ak
    sk = config.sk
    region = config.region
    project_id = config.project_id
    
    print(f"Stopping VM '{vm_name}' in Huawei Cloud...")
    
    # Interactive login
    credentials = BasicCredentials(ak, sk, project_id)
    
    # Create ECS client
    ecs_client = EcsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(EcsRegion.value_of(region)) \
        .build()
    
    try:
        # First search for the VM
        search_result = search_huawei_vm()
        server_id = search_result['server_id']
        current_status = search_result['status']
        
        print(f"Current status: {current_status}")
        
        # Stop the server if not already stopped
        if current_status.upper() in ['ACTIVE', 'RUNNING']:
            from huaweicloudsdkecs.v2 import BatchStopServersRequest, BatchStopServersRequestBody, ServerId, BatchStopServersOption
            
            stop_request = BatchStopServersRequest()
            stop_body = BatchStopServersRequestBody(
                os_stop=BatchStopServersOption(
                    servers=[ServerId(id=server_id)],
                    type="SOFT"  # SOFT for graceful shutdown, HARD for force shutdown
                )
            )
            stop_request.body = stop_body
            
            ecs_client.batch_stop_servers(stop_request)
            
            result = {
                'message': f"VM '{vm_name}' found successfully in Huawei Cloud and stop command issued!",
                'vm_name': vm_name,
                'server_id': server_id,
                'previous_status': current_status,
                'action': 'stopped'
            }
        else:
            result = {
                'message': f"VM '{vm_name}' found successfully in Huawei Cloud but is already {current_status}!",
                'vm_name': vm_name,
                'server_id': server_id,
                'previous_status': current_status,
                'action': 'no action needed'
            }
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to stop VM '{vm_name}': {str(e)}")


def download_huawei_vm():
    """
    Download OS disk from a stopped Huawei Cloud VM.
    Creates image, exports to OBS, and downloads to local disk.
    
    Returns:
        dict: Result with storage location and details
    
    Raises:
        Exception: If download fails
    """
    
    # Get parameters from config
    vm_name = config.vm_name
    ak = config.ak
    sk = config.sk
    region = config.region
    project_id = config.project_id
    obs_bucket = config.obs_bucket
    download_path = config.download_path
    
    # Create download directory
    os.makedirs(download_path, exist_ok=True)
    
    # Define output path (Huawei exports as QCOW2 by default)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.join(download_path, f"{vm_name}_{timestamp}.qcow2")
    
    # Check if already downloaded
    if os.path.exists(output_file_path):
        result = {
            'message': f"VM '{vm_name}' OS disk already downloaded!",
            'vm_name': vm_name,
            'storage_location': output_file_path,
            'file_size_gb': round(os.path.getsize(output_file_path) / (1024**3), 2),
            'status': 'already_exists'
        }
        print(f"OS disk already exists at: {output_file_path}")
        return result
    
    # Check for existing files with same VM name
    existing_files = [f for f in os.listdir(download_path) if f.startswith(vm_name) and f.endswith('.qcow2')]
    if existing_files:
        existing_path = os.path.join(download_path, existing_files[0])
        result = {
            'message': f"VM '{vm_name}' OS disk already downloaded!",
            'vm_name': vm_name,
            'storage_location': existing_path,
            'file_size_gb': round(os.path.getsize(existing_path) / (1024**3), 2),
            'status': 'already_exists'
        }
        print(f"OS disk already exists at: {existing_path}")
        return result
    
    print(f"Downloading OS disk for VM '{vm_name}'...")
    
    # Interactive login
    credentials = BasicCredentials(ak, sk, project_id)
    
    # Create IMS client for image operations
    ims_client = ImsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(ImsRegion.value_of(region)) \
        .build()
    
    # Create OBS client for download
    obs_client = ObsClient(
        access_key_id=ak,
        secret_access_key=sk,
        server=f"https://obs.{region}.myhuaweicloud.com"
    )
    
    image_id = None
    obs_file_key = None
    
    try:
        # Get VM details
        search_result = search_huawei_vm()
        server_id = search_result['server_id']
        vm_size = search_result['vm_size']
        resource_id = search_result['resource_id']
        
        # Check if VM is stopped
        if search_result['status'].upper() not in ['SHUTOFF', 'STOPPED']:
            raise Exception(f"VM must be stopped. Current status: {search_result['status']}")
        
        print("Creating image from VM...")
        
        # Create whole image from server
        from huaweicloudsdkims.v2 import CreateImageRequestBody
        
        image_request = CreateWholeImageRequest()
        image_body = CreateWholeImageRequestBody(
            name=f"{vm_name}_export_{timestamp}",
            instance_id=server_id,
            description=f"Export image for {vm_name}"
        )
        image_request.body = image_body
        
        image_response = ims_client.create_whole_image(image_request)
        image_id = image_response.job_id
        
        print(f"Image creation job started: {image_id}")
        print("Waiting for image creation to complete (this may take several minutes)...")
        
        # Wait for image to be created
        from huaweicloudsdkims.v2 import ShowJobRequest
        
        while True:
            job_request = ShowJobRequest(job_id=image_id)
            job_response = ims_client.show_job(job_request)
            
            status = job_response.status
            print(f"Image creation status: {status}")
            
            if status == 'SUCCESS':
                # Get the actual image ID from job
                if job_response.entities and 'image_id' in job_response.entities:
                    image_id = job_response.entities['image_id']
                print(f"Image created successfully: {image_id}")
                break
            elif status == 'FAIL':
                raise Exception("Image creation failed")
            
            time.sleep(15)
        
        # Export image to OBS
        print(f"Exporting image to OBS bucket: {obs_bucket}...")
        
        from huaweicloudsdkims.v2 import ExportImageRequest, ExportImageRequestBody
        
        obs_file_key = f"exports/{vm_name}_{timestamp}.qcow2"
        
        export_request = ExportImageRequest(image_id=image_id)
        export_body = ExportImageRequestBody(
            bucket_url=obs_bucket,
            file_format="qcow2",  # QCOW2 is native format
            image_id=image_id
        )
        export_request.body = export_body
        
        export_response = ims_client.export_image(export_request)
        export_job_id = export_response.job_id
        
        print(f"Export job started: {export_job_id}")
        print("Waiting for export to complete...")
        
        # Wait for export to complete
        while True:
            job_request = ShowJobRequest(job_id=export_job_id)
            job_response = ims_client.show_job(job_request)
            
            status = job_response.status
            print(f"Export status: {status}")
            
            if status == 'SUCCESS':
                print("Export completed!")
                break
            elif status == 'FAIL':
                raise Exception("Export failed")
            
            time.sleep(20)
        
        # Download from OBS
        print(f"Downloading from OBS: {obs_bucket}/{obs_file_key}...")
        print(f"Saving to: {output_file_path}")
        
        # Download file
        resp = obs_client.getObject(obs_bucket, obs_file_key, downloadPath=output_file_path)
        
        if resp.status >= 300:
            raise Exception(f"Failed to download from OBS: {resp.errorMessage}")
        
        print("Download completed!")
        
        # Get file size
        file_size_gb = round(os.path.getsize(output_file_path) / (1024**3), 2)
        
        # Clean up OBS (optional)
        print("Cleaning up OBS...")
        obs_client.deleteObject(obs_bucket, obs_file_key)
        
        # Clean up image (optional)
        print("Cleaning up image...")
        from huaweicloudsdkims.v2 import DeleteImageRequest
        delete_request = DeleteImageRequest(image_id=image_id)
        ims_client.delete_image(delete_request)
        
        result = {
            'message': f"VM '{vm_name}' OS disk downloaded successfully from Huawei Cloud!",
            'vm_name': vm_name,
            'vm_size': vm_size,
            'resource_id': resource_id,
            'storage_location': output_file_path,
            'file_size_gb': file_size_gb,
            'file_format': 'QCOW2',
            'status': 'download_completed'
        }
        
        return result
        
    except Exception as e:
        # Clean up on error
        print(f"\nError occurred: {str(e)}")
        print("Cleaning up resources...")
        
        try:
            if obs_file_key:
                obs_client.deleteObject(obs_bucket, obs_file_key)
                print("OBS object deleted")
        except:
            pass
        
        try:
            if image_id:
                from huaweicloudsdkims.v2 import DeleteImageRequest
                delete_request = DeleteImageRequest(image_id=image_id)
                ims_client.delete_image(delete_request)
                print("Image deleted")
        except:
            pass
        
        raise Exception(f"Failed to download OS disk for VM '{vm_name}': {str(e)}")
    
    finally:
        obs_client.close()


# Example usage
if __name__ == "__main__":
    print("=== STEP 1: Search for VM ===")
    try:
        search_result = search_huawei_vm()
        print(search_result['message'])
        print(f"VM Size: {search_result['vm_size']}")
        print(f"Status: {search_result['status']}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    
    print("\n=== STEP 2: Stop VM ===")
    try:
        stop_result = stop_huawei_vm()
        print(stop_result['message'])
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    
    print("\n=== STEP 3: Download VM ===")
    try:
        download_result = download_huawei_vm()
        print(download_result['message'])
        print(f"Storage Location: {download_result['storage_location']}")
        print(f"File Size: {download_result['file_size_gb']} GB")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
