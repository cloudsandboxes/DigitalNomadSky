def upload_disk(shared_data):
    
    import sys
    sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
    from azure.mgmt.storage import StorageManagementClient
    from azure.storage.blob import BlobServiceClient, BlobClient
    import os
    from azure.identity import InteractiveBrowserCredential
    import config


    # Variables
    subscription_id = config.subscription_id
    resource_group = config.resource_group
    storage_account_name = config.storage_account_name 
    location = config.location 
    container_name = config.container_name
    vhd_path = shared_data.get('output_vhd_path', '')
    blob_name = config.blob_name

    tenant_id = config.destionationtenantid
    credential = InteractiveBrowserCredential(tenant_id=tenant_id)

    # Create storage account
    storage_client = StorageManagementClient(credential, subscription_id)
    try:
        storage_client.storage_accounts.get_properties(resource_group, storage_account_name)
        #print("Storage account already exists")
    except ResourceNotFoundError:
        #print("Creating storage account...")
        storage_client.storage_accounts.begin_create(
            resource_group,
            storage_account_name,
            {
                "sku": {"name": "Standard_LRS"},
                "kind": "StorageV2",
                "location": location
            }
        ).result()
        #print("Storage account created")

    # Get storage account key
    keys = storage_client.storage_accounts.list_keys(resource_group, storage_account_name)
    storage_key = keys.keys[0].value

    # Create blob container
    blob_service = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=storage_key
    )
    container_client = blob_service.get_container_client(container_name)
    try:
        container_client.get_container_properties()
        #print("Container already exists")
    except ResourceNotFoundError:
        #print("Creating container...")
        blob_service.create_container(container_name)
        #print("Container created")

    # Upload VHD
    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
    try:
        blob_client.get_blob_properties()
        #print("Blob already exists")
    except ResourceNotFoundError:
        #print("Uploading VHD...")
        with open(vhd_path, "rb") as data:
            blob_client.upload_blob(data, blob_type="PageBlob", overwrite=False)
        #print(f"VHD uploaded: {blob_client.url}")
    return account_url
    
