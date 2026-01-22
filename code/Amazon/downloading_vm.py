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
    import time
    from datetime import datetime

    sys.path.append(r"C:/projects/nomadsky/code/Amazon")
    import config
    
    # Get parameters from config
    source = sys.argv[1]
    destination = sys.argv[2]
    vm_name = sys.argv[3].lower()
    
    # Get parameters from config
    region = shared_data.get('region', '')
    vm_size = shared_data.get('vm_size', '')
    resource_id = shared_data.get('resource_id', '')
    download_path = config.download_path
    s3_bucket_name = config.s3_bucket_name
    
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
    if os.path.exists(output_vhd_path):
        result = {
            'message': f"VM '{vm_name}' OS disk already downloaded!",
            'vm_name': vm_name,
            'vm_size': vm_size,
            'resource_id': resource_id,
            'storage_location': output_vhd_path,
            'file_size_gb': round(os.path.getsize(output_vhd_path) / (1024**3), 2),
            'status': 'already_exists'
        }
        print(f"OS disk already exists at: {output_vhd_path}")
        return result
    
    # Check for any existing files with same VM name
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
    s3_client = session.client('s3', region_name=region)
    
    snapshot_id = None
    export_task_id = None
    s3_key = None
    
    try:
        # Get instance details
        print("Checking instance state...")
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        
        # Check if instance is stopped/deallocated
        state = instance['State']['Name']
        if state not in ['stopped', 'stopping']:
            raise Exception(f"VM must be stopped to download disk. Current state: {state}")
        
        print(f"Instance state: {state}")
        
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
        
        # Get volume size
        volume_details = ec2_client.describe_volumes(VolumeIds=[volume_id])
        volume_size_gb = volume_details['Volumes'][0]['Size']
        
        # Create or verify S3 bucket
        print(f"Checking S3 bucket: {s3_bucket_name}...")
        try:
            s3_client.head_bucket(Bucket=s3_bucket_name)
            print("S3 bucket exists")
        except:
            print(f"Creating S3 bucket: {s3_bucket_name}...")
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=s3_bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=s3_bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            print("S3 bucket created")
        
        # Create snapshot of the volume
        print("Creating snapshot of OS disk...")
        snapshot_response = ec2_client.create_snapshot(
            VolumeId=volume_id,
            Description=f"Snapshot for {vm_name} download - {timestamp}"
        )
        snapshot_id = snapshot_response['SnapshotId']
        
        print(f"Snapshot created: {snapshot_id}. Waiting for completion...")
        
        # Wait for snapshot to complete (with progress updates)
        while True:
            snapshot_status = ec2_client.describe_snapshots(SnapshotIds=[snapshot_id])
            progress = snapshot_status['Snapshots'][0]['Progress']
            state = snapshot_status['Snapshots'][0]['State']
            
            print(f"Snapshot progress: {progress} - State: {state}")
            
            if state == 'completed':
                print("Snapshot completed!")
                break
            elif state == 'error':
                raise Exception("Snapshot creation failed")
            
            time.sleep(15)
        
        # Export snapshot to S3
        print("Starting export to S3...")
        s3_key = f"exports/{vm_name}_{timestamp}.vhd"
        
        export_response = ec2_client.create_instance_export_task(
            Description=f"Export {vm_name} OS disk",
            ExportToS3Task={
                'DiskImageFormat': 'VHD',
                'S3Bucket': s3_bucket_name,
                'S3Prefix': f'exports/{vm_name}_{timestamp}'
            },
            InstanceId=instance_id,
            TargetEnvironment='microsoft'
        )
        
        export_task_id = export_response['ExportTask']['ExportTaskId']
        print(f"Export task created: {export_task_id}")
        
        # Wait for export to complete
        print("Waiting for export to complete (this may take a while)...")
        while True:
            export_status = ec2_client.describe_export_tasks(ExportTaskIds=[export_task_id])
            state = export_status['ExportTasks'][0]['State']
            status_message = export_status['ExportTasks'][0].get('StatusMessage', '')
            
            print(f"Export state: {state} - {status_message}")
            
            if state == 'completed':
                print("Export completed!")
                break
            elif state in ['cancelled', 'cancelling']:
                raise Exception("Export task was cancelled")
            
            time.sleep(30)
        
        # Get the actual S3 key from export task
        export_details = ec2_client.describe_export_tasks(ExportTaskIds=[export_task_id])
        s3_bucket = export_details['ExportTasks'][0]['ExportToS3Task']['S3Bucket']
        s3_key = export_details['ExportTasks'][0]['ExportToS3Task']['S3Key']
        
        # Download from S3
        print(f"Downloading from S3: s3://{s3_bucket}/{s3_key}...")
        print(f"Saving to: {output_vhd_path}")
        
        # Download with progress
        s3_client.download_file(
            s3_bucket, 
            s3_key, 
            output_vhd_path,
            Callback=lambda bytes_transferred: print(f"Downloaded: {bytes_transferred / (1024**2):.2f} MB", end='\r')
        )
        
        print(f"\nDownload completed!")
        
        # Get final file size
        file_size_gb = round(os.path.getsize(output_vhd_path) / (1024**3), 2)
        
        # Clean up S3 (optional - comment out if you want to keep the file in S3)
        print("Cleaning up S3...")
        s3_client.delete_object(Bucket=s3_bucket, Key=s3_key)
        
        # Clean up snapshot (optional - comment out if you want to keep the snapshot)
        print("Cleaning up snapshot...")
        ec2_client.delete_snapshot(SnapshotId=snapshot_id)
        
        result = {
            'message': f"VM '{vm_name}' OS disk downloaded successfully from AWS!",
            'vm_name': vm_name,
            'vm_size': vm_size,
            'resource_id': resource_id,
            'storage_location': output_vhd_path,
            'file_size_gb': file_size_gb,
            'disk_size_gb': volume_size_gb,
            'snapshot_id': snapshot_id,
            'volume_id': volume_id,
            'status': 'download_completed'
        }
        
        return result
        
    except Exception as e:
        # Clean up on error
        print(f"\nError occurred: {str(e)}")
        print("Cleaning up resources...")
        
        try:
            if s3_key:
                s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_key)
                print("S3 object deleted")
        except:
            pass
        
        try:
            if snapshot_id:
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                print("Snapshot deleted")
        except:
            pass
        
        raise Exception(f"Failed to download OS disk for VM '{vm_name}': {str(e)}")


# Example usage
if __name__ == "__main__":
    try:
        result = download_aws_osdisk()
        print("\n" + "="*60)
        print(result['message'])
        print(f"VM Name: {result['vm_name']}")
        print(f"VM Size: {result['vm_size']}")
        print(f"Storage Location: {result['storage_location']}")
        print(f"File Size: {result['file_size_gb']} GB")
        print(f"Status: {result['status']}")
        print("="*60)
    except Exception as e:
        print(f"Error: {e}")
