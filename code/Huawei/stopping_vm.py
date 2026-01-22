def stop_huawei_vm(shared_data):
    """
    Stop a VM in Huawei Cloud.
    
    Returns:
        dict: Result with message about stop operation
    
    Raises:
        Exception: If VM not found or stop fails
    """
    
    # Get parameters from config
    ak = config.ak
    sk = config.sk
    region = config.region
    project_id = config.project_id
    source = sys.argv[1]
    destination = sys.argv[2]
    vm_name = sys.argv[3].lower()
    
    # Get parameters from config
    vm_size = shared_data.get('vm_size', '')
    
    #print(f"Stopping VM '{vm_name}' in Huawei Cloud...")
    
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
        
        #print(f"Current status: {current_status}")
        
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

