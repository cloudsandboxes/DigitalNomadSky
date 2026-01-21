from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient, BlobClient
import os

# Variables
subscription_id = "your-subscription-id"
resource_group = "your-resource-group"
storage_account_name = "yourstorageaccount"
location = "westeurope"
container_name = "vhds"
vhd_path = "c:/temp/osdisk.vhd"
blob_name = "osdisk.vhd"

credential = DefaultAzureCredential()

# Create storage account
storage_client = StorageManagementClient(credential, subscription_id)
storage_client.storage_accounts.begin_create(
    resource_group,
    storage_account_name,
    {
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2",
        "location": location
    }
).result()

# Get storage account key
keys = storage_client.storage_accounts.list_keys(resource_group, storage_account_name)
storage_key = keys.keys[0].value

# Create blob container
blob_service = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=storage_key
)
container_client = blob_service.create_container(container_name)

# Upload VHD
blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
with open(vhd_path, "rb") as data:
    blob_client.upload_blob(data, blob_type="PageBlob", overwrite=True)

print(f"VHD uploaded: {blob_client.url}")
