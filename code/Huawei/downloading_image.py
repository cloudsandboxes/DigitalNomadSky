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

