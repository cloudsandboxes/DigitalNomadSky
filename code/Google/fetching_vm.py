"""
Google Cloud Platform VM Management Script

Required pip packages:
py -m pip install google-cloud-compute
py -m pip install google-cloud-storage
py -m pip install google-auth

Required config.py file at C:/projects/nomadsky/code/gcp/config.py with:
vm_name = "your-vm-name"
project_id = "your-project-id"
zone = "europe-west1-b"  # optional, if None searches all zones
gcs_bucket = "vm-export-bucket"
download_path = "C:/temp"
credentials_path = "C:/path/to/service-account-key.json"

Note: GCP supports VMDK and VHD formats for export.
VMDK is recommended for GCP native format.
"""

import sys
import os
import time
from datetime import datetime

# GCP imports
from google.cloud import compute_v1
from google.cloud import storage
from google.oauth2 import service_account

sys.path.append(r"C:/projects/nomadsky/code/gcp")
import config


def search_gcp_vm():
    """
    Search for a VM in Google Cloud Platform by name.
    
    Returns:
        dict: VM details including id, size, os, and disk information
    
    Raises:
        Exception: If VM not found
    """
    
    # Get parameters from config
    vm_name = config.vm_name
    project_id = config.project_id
    zone = getattr(config, 'zone', None)
    credentials_path = config.credentials_path
    
    print(f"Searching for VM '{vm_name}' in GCP...")
    
    # Interactive login
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    
    # Create compute client
    instances_client = compute_v1.InstancesClient(credentials=credentials)
    
    # Determine zones to search
    if zone:
        zones_to_search = [zone]
    else:
        zones_client = compute_v1.ZonesClient(credentials=credentials)
        zones_list = zones_client.list(project=project_id)
        zones_to_search = [z.name for z in zones_list]
    
    try:
        # Search for instance
        for search_zone in zones_to_search:
            try:
                request = compute_v1.GetInstanceRequest(
                    project=project_id,
                    zone=search_zone,
                    instance=vm_name
                )
                
                instance = instances_client.get(request=request)
                
                # Extract instance details
                instance_id = str(instance.id)
                machine_type = instance.machine_type.split('/')[-1]
                status = instance.status
                
                # Determine OS type from disks
                os_type = "Linux"
                disks = []
                
                for disk in instance.disks:
                    disk_info = {
                        'device_name': disk.device_name,
                        'source': disk.source.split('/')[-1],
                        'boot': disk.boot,
                        'auto_delete': disk.auto_delete,
                        'mode': disk.mode
                    }
                    
                    # Get disk details
                    if disk.source:
                        disk_name = disk.source.split('/')[-1]
                        disk_zone = disk.source.split('/')[-3]
                        
                        disks_client = compute_v1.DisksClient(credentials=credentials)
                        disk_request = compute_v1.GetDiskRequest(
                            project=project_id,
                            zone=disk_zone,
                            disk=disk_name
                        )
                        disk_details = disks_client.get(request=disk_request)
                        
                        disk_info['size_gb'] = disk_details.size_gb
                        disk_info['type'] = disk_details.type.split('/')[-1]
                        
                        # Determine OS from source image
                        if disk.boot and disk_details.source_image:
                            if 'windows' in disk_details.source_image.lower():
                                os_type = "Windows"
                    
                    disks.append(disk_info)
                
                result = {
                    'message': f"VM '{vm_name}' found successfully in GCP!",
                    'source': 'Google Cloud Platform',
                    'vm_name': vm_name,
                    'instance_id': instance_id,
                    'vm_size': machine_type,
                    'status': status,
                    'os_type': os_type,
                    'resource_id': f"projects/{project_id}/zones/{search_zone}/instances/{vm_name}",
                    'zone': search_zone,
                    'project_id': project_id,
                    'disk_details': disks
                }
                
                print(f"VM found in zone {search_zone}")
                return result
                
            except Exception:
                continue
        
        raise Exception(f"VM '{vm_name}' not found in any zone")
        
    except Exception as e:
        raise Exception(f"Failed to search for VM '{vm_name}': {str(e)}")


def stop_gcp_vm():
    """
    Stop a VM in Google Cloud Platform.
    
    Returns:
        dict: Result with message about stop operation
    
    Raises:
        Exception: If VM not found or stop fails
    """
    
    # Get parameters from config
    vm_name = config.vm_name
    project_id = config.project_id
    credentials_path = config.credentials_path
    
    print(f"Stopping VM '{vm_name}' in GCP...")
    
    # Interactive login
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    
    # Create compute client
    instances_client = compute_v1.InstancesClient(credentials=credentials)
    
    try:
        # First search for the VM
        search_result = search_gcp_vm()
        zone = search_result['zone']
        current_status = search_result['status']
        
        print(f"Current status: {current_status}")
        
        # Stop the instance if running
        if current_status == 'RUNNING':
            request = compute_v1.StopInstanceRequest(
                project=project_id,
                zone=zone,
                instance=vm_name
            )
            
            operation = instances_client.stop(request=request)
            
            # Wait for operation to complete
            print("Waiting for stop operation to complete...")
            operation.result()
            
            result = {
                'message': f"VM '{vm_name}' found successfully in GCP and stop command issued!",
                'vm_name': vm_name,
                'instance_id': search_result['instance_id'],
                'zone': zone,
                'previous_status': current_status,
                'action': 'stopped'
            }
        else:
            result = {
                'message': f"VM '{vm_name}' found successfully in GCP but is already {current_status}!",
                'vm_name': vm_name,
                'instance_id': search_result['instance_id'],
                'zone': zone,
                'previous_status': current_status,
                'action': 'no action needed'
            }
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to stop VM '{vm_name}': {str(e)}")


def download_gcp_vm():
    """
    Download OS disk from a stopped GCP VM.
    Creates image, exports to GCS, and downloads to local disk.
    
    Returns:
        dict: Result with storage location and details
    
    Raises:
        Exception: If download fails
    """
    
    # Get parameters from config
    vm_name = config.vm_name
    project_id = config.project_id
    gcs_bucket = config.gcs_bucket
    download_path = config.download_path
    credentials_path = config.credentials_path
    
    # Create download directory
    os.makedirs(download_path, exist_ok=True)
    
    # Define output path (GCP exports as VMDK by default)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_path = os.path.join(download_path, f"{vm_name}_{timestamp}.vmdk")
    
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
    existing_files = [f for f in os.listdir(download_path) if f.startswith(vm_name) and f.endswith('.vmdk')]
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
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    
    # Create clients
    images_client = compute_v1.ImagesClient(credentials=credentials)
    storage_client = storage.Client(credentials=credentials, project=project_id)
    
    image_name = None
    gcs_file_path = None
    
    try:
        # Get VM details
        search_result = search_gcp_vm()
        zone = search_result['zone']
        vm_size = search_result['vm_size']
        resource_id = search_result['resource_id']
        
        # Check if VM is stopped
        if search_result['status'] != 'TERMINATED':
            raise Exception(f"VM must be stopped. Current status: {search_result['status']}")
        
        # Get boot disk
        boot_disk = None
        for disk in search_result['disk_details']:
            if disk['boot']:
                boot_disk = disk['source']
                break
        
        if not boot_disk:
            raise Exception("Could not find boot disk")
        
        print(f"Boot disk: {boot_disk}")
        
        # Create image from disk
        image_name = f"{vm_name}-export-{timestamp}".replace('_', '-').lower()
        print(f"Creating image '{image_name}' from disk...")
        
        image_body = compute_v1.Image(
            name=image_name,
            source_disk=f"projects/{project_id}/zones/{zone}/disks/{boot_disk}"
        )
        
        request = compute_v1.InsertImageRequest(
            project=project_id,
            image_resource=image_body
        )
        
        operation = images_client.insert(request=request)
        
        print("Waiting for image creation to complete...")
        operation.result()
        print(f"Image created: {image_name}")
        
        # Export image to GCS
        gcs_file_path = f"exports/{vm_name}_{timestamp}"
        gcs_uri = f"gs://{gcs_bucket}/{gcs_file_path}"
        
        print(f"Exporting image to GCS: {gcs_uri}...")
        
        # Create export request
        export_request = compute_v1.ExportImageRequest(
            project=project_id,
            image=image_name,
            image_export_request_resource=compute_v1.ImageExportRequest(
                destination_uri=gcs_uri,
                disk_image_format="vmdk"  # or "vhdx"
            )
        )
        
        export_operation = images_client.export(request=export_request)
        
        print("Waiting for export to complete (this may take a while)...")
        export_operation.result()
        print("Export completed!")
        
        # Download from GCS
        print(f"Downloading from GCS bucket: {gcs_bucket}...")
        
        bucket = storage_client.bucket(gcs_bucket)
        
        # Find the actual blob (GCP adds extensions)
        blobs = list(bucket.list_blobs(prefix=gcs_file_path))
        
        if not blobs:
            raise Exception("Export file not found in GCS bucket")
        
        # Download the first blob (main disk file)
        blob = blobs[0]
        actual_filename = blob.name.split('/')[-1]
        
        print(f"Downloading {blob.name}...")
        blob.download_to_filename(output_file_path)
        
        print("Download completed!")
        
        # Get file size
        file_size_gb = round(os.path.getsize(output_file_path) / (1024**3), 2)
        
        # Clean up GCS (optional)
        print("Cleaning up GCS...")
        for blob in blobs:
            blob.delete()
        
        # Clean up image (optional)
        print("Cleaning up image...")
        delete_request = compute_v1.DeleteImageRequest(
            project=project_id,
            image=image_name
        )
        images_client.delete(request=delete_request)
        
        result = {
            'message': f"VM '{vm_name}' OS disk downloaded successfully from GCP!",
            'vm_name': vm_name,
            'vm_size': vm_size,
            'resource_id': resource_id,
            'storage_location': output_file_path,
            'file_size_gb': file_size_gb,
            'file_format': 'VMDK',
            'status': 'download_completed'
        }
        
        return result
        
    except Exception as e:
        # Clean up on error
        print(f"\nError occurred: {str(e)}")
        print("Cleaning up resources...")
        
        try:
            if gcs_file_path:
                bucket = storage_client.bucket(gcs_bucket)
                blobs = list(bucket.list_blobs(prefix=gcs_file_path))
                for blob in blobs:
                    blob.delete()
                print("GCS objects deleted")
        except:
            pass
        
        try:
            if image_name:
                delete_request = compute_v1.DeleteImageRequest(
                    project=project_id,
                    image=image_name
                )
                images_client.delete(request=delete_request)
                print("Image deleted")
        except:
            pass
        
        raise Exception(f"Failed to download OS disk for VM '{vm_name}': {str(e)}")


# Example usage
if __name__ == "__main__":
    print("=== STEP 1: Search for VM ===")
    try:
        search_result = search_gcp_vm()
        print(search_result['message'])
        print(f"VM Size: {search_result['vm_size']}")
        print(f"Status: {search_result['status']}")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    
    print("\n=== STEP 2: Stop VM ===")
    try:
        stop_result = stop_gcp_vm()
        print(stop_result['message'])
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    
    print("\n=== STEP 3: Download VM ===")
    try:
        download_result = download_gcp_vm()
        print(download_result['message'])
        print(f"Storage Location: {download_result['storage_location']}")
        print(f"File Size: {download_result['file_size_gb']} GB")
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
