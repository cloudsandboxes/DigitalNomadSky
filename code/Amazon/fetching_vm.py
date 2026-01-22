
def search_ec2_instance(vm_name: str):
    """
    Search for an EC2 instance by name across all available AWS accounts.
    Uses interactive SSO login.
    
    Args:
        vm_name: Name of the EC2 instance to search for (Name tag value)
    
    Returns:
        dict: Instance details including ID, size, OS, and disk information
    
    Raises:
        Exception: If instance not found in any account
    """
    
    # Interactive SSO login
    session = boto3.Session()
    
    # Get available accounts via Organizations (if you have access)
    # If not using Organizations, you'll need to specify accounts manually
    import boto3
    import json

    source = sys.argv[1]
    destination = sys.argv[2]
    vmname = sys.argv[3].lower()
    
    try:
        org_client = session.client('organizations')
        accounts_response = org_client.list_accounts()
        accounts = [acc['Id'] for acc in accounts_response['Accounts'] if acc['Status'] == 'ACTIVE']
    except Exception as e:
        print(f"Could not list organization accounts: {e}")
        print("Searching in current account only...")
        accounts = [session.client('sts').get_caller_identity()['Account']]
    
    # Search across all regions and accounts
    ec2_client = session.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    
    print(f"Searching for VM '{vm_name}' across {len(accounts)} account(s) and {len(regions)} region(s)...")
    
    for account_id in accounts:
        for region in regions:
            try:
                # Create regional EC2 client
                regional_client = session.client('ec2', region_name=region)
                
                # Search for instance by Name tag
                response = regional_client.describe_instances(
                    Filters=[
                        {'Name': 'tag:Name', 'Values': [vm_name]},
                        {'Name': 'instance-state-name', 'Values': ['running', 'stopped', 'stopping', 'pending']}
                    ]
                )
                
                # Check if instance found
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        # Extract instance details
                        instance_id = instance['InstanceId']
                        instance_type = instance['InstanceType']
                        state = instance['State']['Name']
                        
                        # Determine OS type from platform or image
                        platform = instance.get('Platform', 'Linux')
                        if platform == 'windows':
                            os_type = 'Windows'
                        else:
                            os_type = 'Linux'
                        
                        # Get disk details
                        disks = []
                        for bdm in instance.get('BlockDeviceMappings', []):
                            if 'Ebs' in bdm:
                                volume_id = bdm['Ebs']['VolumeId']
                                
                                # Get volume details
                                volume = regional_client.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
                                
                                disk_info = {
                                    'device_name': bdm['DeviceName'],
                                    'volume_id': volume_id,
                                    'size_gb': volume['Size'],
                                    'volume_type': volume['VolumeType'],
                                    'iops': volume.get('Iops'),
                                    'encrypted': volume['Encrypted']
                                }
                                disks.append(disk_info)
                        
                        # Build result
                        result = {
                            'message': f"VM '{vm_name}' found successfully in AWS!",
                            'source': 'AWS',
                            'account_id': account_id,
                            'region': region,
                            'instance_id': instance_id,
                            'resource_id': f"arn:aws:ec2:{region}:{account_id}:instance/{instance_id}",
                            'vm_size': instance_type,
                            'state': state,
                            'os_type': os_type,
                            'private_ip': instance.get('PrivateIpAddress'),
                            'public_ip': instance.get('PublicIpAddress'),
                            'availability_zone': instance['Placement']['AvailabilityZone'],
                            'disk_details': disks,
                            'tags': instance.get('Tags', [])
                        }
                        
                        print(f"Instance found in account {account_id}, region {region}")
                        return result
                        
            except Exception as e:
                # Skip regions/accounts we don't have access to
                continue
    
    # If we get here, instance was not found
    raise Exception(f"VM '{vm_name}' not found in any available AWS account or region")


