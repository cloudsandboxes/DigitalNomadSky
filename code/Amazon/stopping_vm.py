"""
AWS EC2 Instance Stop Script

Required pip packages:
py -m pip install boto3

Required config.py file at C:/projects/nomadsky/code/Amazon/config.py with:
vm_name = "your-instance-name"
resource_id = "arn:aws:ec2:region:account:instance/i-xxxxx" or instance_id
region = "eu-west-1"
vm_size = "t3.medium"
"""


def stop_aws_vm():
    """
    Stop an AWS EC2 instance based on stored details from config.
    Uses interactive AWS login.
    
    Returns:
        dict: Result containing message, vm_size, and resource_id
    
    Raises:
        Exception: If stop operation fails
    """
    import sys
    import boto3
    sys.path.append(r"C:/projects/nomadsky/code/Amazon")
    import config
    source = sys.argv[1]
    destination = sys.argv[2]
    vmname = sys.argv[3].lower()
    
    # Get parameters from config
    vm_name = config.vm_name
    region = config.region
    vm_size = config.vm_size
    resource_id = config.resource_id
    
    # Extract instance ID from resource_id if it's an ARN
    if resource_id.startswith('arn:'):
        instance_id = resource_id.split('/')[-1]
    else:
        instance_id = resource_id
    
    print(f"Stopping VM '{vm_name}' (Instance: {instance_id}) in region {region}...")
    
    # Interactive login via boto3
    session = boto3.Session()
    ec2_client = session.client('ec2', region_name=region)
    
    try:
        # Stop the instance
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        
        current_state = response['StoppingInstances'][0]['CurrentState']['Name']
        previous_state = response['StoppingInstances'][0]['PreviousState']['Name']
        
        result = {
            'message': f"VM '{vm_name}' found successfully in AWS and stop command issued!",
            'vm_size': vm_size,
            'resource_id': resource_id,
            'instance_id': instance_id,
            'region': region,
            'previous_state': previous_state,
            'current_state': current_state
        }
        
        return result
        
    except Exception as e:
        raise Exception(f"Failed to stop VM '{vm_name}': {str(e)}")
