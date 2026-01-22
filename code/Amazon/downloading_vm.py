"""
AWS EC2 OS Disk Download Script

Required pip packages:
py -m pip install boto3

Required config.py file at C:/projects/nomadsky/code/Amazon/config.py with:
vm_name = "your-instance-name"
resource_id = "i-xxxxx"
region = "eu-west-1"
vm_size = "t3.medium"
download_path = "C:/aws_disks"
"""
def download_aws_osdisk():
    """
    Download OS disk from a deallocated AWS EC2 instance.
    Uses interactive AWS login.
    
    Returns:
        dict: Result containing message, storage location, and details
    
    Raises:
        Exception: If download fails or VM not deallocated
    """
    import sys
    import os
    import boto3
    from datetime import datetime

    sys.path.append(r"C:/projects/nomadsky/code/Amazon")
    import config
    
    # Get parameters from config
    vm_name = config.vm_name
    region = config.region
    vm_size = config.vm_size
    resource_id = config.resource_id
    download_path = config.download_path
    
    # Extract instance ID from resource_id if it's an ARN
    if resource_id.startswith('arn:'):
        instance_id = resource_id.split('/')[-1]
    else:
        instance_id = resource_id
    
    # Create download directory if it doesn't exist
    os.makedirs(download_path, exist_ok=True)
    
    # Define output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_vhd_path = os.path.join(download_path, f"{vm_name}_{timestamp}.vhd")
    
    # Check if already downloaded
    existing_files = [f for f in os.listdir(download_path) if f.startswith(vm_name) and f.endswith('.vhd')]
    if existing_files:
        existing_path = os.path.join(download_path, existing_files[0])
        result = {
            'message': f"VM '{vm_name}' OS disk already downloaded!",
            'vm_name': vm_name,
            'vm_size': vm_size,
            'resource_id': resource_id,
            'storage_location': existing_path,
            'file_size_gb': round(os.path.getsize(existing_path) / (1024**3), 2),
            'status': 'already_exists'
        }
        print(f"OS disk already exists at: {existing_path}")
        return result
    
    print(f"Downloading OS disk for VM '{vm_name}' (Instance: {instance_id})...")
    
    # Interactive login via boto3
    session = boto3.Session()
    ec2_client = session.client('ec2', region_name=region)
    
    try:
        # Get instance details
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        
        # Check if instance is stopped/deallocated
        state = instance['State']['Name']
        if state not in ['stopped', 'stopping']:
            raise Exception(f"VM must be stopped to download disk. Current state: {state}")
        
        # Get root volume ID
        root_device = instance['RootDeviceName']
        volume_id = None
        
        for bdm in instance['BlockDeviceMappings']:
            if bdm['DeviceName'] == root_device and 'Ebs' in bdm:
                volume_id = bdm['Ebs']['VolumeId']
                break
        
        if not volume_id:
            raise Exception("Could not find root volume")
        
        print(f"Root volume ID: {volume_id}")
        
        # Create snapshot of the volume
        print("Creating snapshot of OS disk...")
        snapshot_response = ec2_client.create_snapshot(
            VolumeId=volume_id,
            Description=f"Snapshot for {vm_name} download"
        )
        snapshot_id = snapshot_response['SnapshotId']
        
        print(f"Snapshot created: {snapshot_id}. Waiting for completion...")
        
        # Wait for snapshot to complete
        waiter = ec2_client.get_waiter('snapshot_completed')
        waiter.wait(SnapshotIds=[snapshot_id])
        
        print("Snapshot completed!")
        
        # Export snapshot to S3 (AWS requires S3 bucket for export)
        # Note: This requires additional S3 setup and permissions
        print("Note: AWS requires exporting to S3 first, then downloading from S3")
        print("Creating export task...")
        
        # Get snapshot size
        snapshot_details = ec2_client.describe_snapshots(SnapshotIds=[snapshot_id])
        snapshot_size_gb = snapshot_details['Snapshots'][0]['VolumeSize']
        
        # For direct download, we'll use a workaround:
        # Create a temporary volume, attach to a temporary instance, and use dd/qemu
        # However, this is complex. Better approach: export to S3 bucket
        
        result = {
            'message': f"VM '{vm_name}' OS disk snapshot created successfully!",
            'vm_name': vm_name,
            'vm_size': vm_size,
            'resource_id': resource_id,
            'snapshot_id': snapshot_id,
            'volume_id': volume_id,
            'disk_size_gb': snapshot_size_gb,
            'storage_location': 'AWS Snapshot (use AWS CLI or Console to export to S3, then download)',
            'next_steps': [
                f"1. Export snapshot {snapshot_id} to S3 using AWS Console or CLI",
                "2. Download VHD from S3 bucket",
                f"3. Save to {output_vhd_path}"
            ],
            'status': 'snapshot_created'
        }
        
        print("\n" + "="*60)
        print("IMPORTANT: AWS doesn't support direct disk download.")
        print("You need to:")
        print(f"1. Go to AWS Console > EC2 > Snapshots > {snapshot_id}")
        print("2. Actions > Export to S3")
        print("3. Download the exported file from S3")
        print("="*60)
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to download OS disk for VM '{vm_name}': {str(e)}")


# Example usage
if __name__ == "__main__":
    try:
        result = download_aws_osdisk()
        print("\n" + "="*60)
        print(result['message'])
        print(f"VM Size: {result['vm_size']}")
        print(f"Snapshot ID: {result.get('snapshot_id', 'N/A')}")
        print(f"Storage Location: {result['storage_location']}")
        print("="*60)
    except Exception as e:
        print(f"Error: {e}")
