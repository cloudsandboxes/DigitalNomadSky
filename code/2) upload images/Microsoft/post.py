"""
Before running, install dependencies:

pip install azure-identity azure-storage-blob requests
"""
import requests
import time
import json
import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient

# -------------------------------
# VARIABLES
# -------------------------------
subscription_id = "<SUBSCRIPTION_ID>"
resource_group  = "<RESOURCE_GROUP>"  # Can be new or existing
location        = "westeurope"

# Storage Account
storage_account_name = f"vmstg{os.urandom(4).hex()}"  # Must be globally unique, 3-24 chars, lowercase
container_name = "vhds"

# VNet and Subnet
vnet_name = "new-vnet"
subnet_name = "default"
vnet_address_prefix = "10.0.0.0/16"
subnet_address_prefix = "10.0.1.0/24"

# New VM Configuration
new_vm_name = "<NEW_VM_NAME>"
vm_size = "Standard_D2s_v3"
local_vhd_path = r"C:\Temp\osdisk.vhd"

# Disk and Image names
disk_name = f"{new_vm_name}-osdisk"
image_name = f"{new_vm_name}-image"

# Network interface
nic_name = f"{new_vm_name}-nic"
public_ip_name = f"{new_vm_name}-pip"
nsg_name = f"{new_vm_name}-nsg"

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def get_headers(credential):
    """Get fresh authorization headers"""
    token = credential.get_token("https://management.azure.com/.default").token
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def poll_async_operation(operation_url, credential, timeout=1800, poll_interval=5):
    """Poll an Azure async operation until complete"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        headers = get_headers(credential)
        resp = requests.get(operation_url, headers=headers)
        resp.raise_for_status()
        
        # Handle different response formats
        resp_json = resp.json()
        status = resp_json.get("status", "Unknown")
        
        print(f"  Status: {status}")
        
        if status == "Succeeded":
            return resp_json
        elif status in ["Failed", "Canceled"]:
            error_msg = resp_json.get("error", {})
            raise Exception(f"Operation {status}: {error_msg}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Operation timed out after {timeout} seconds")

def create_or_update_resource(uri, body, credential, resource_name):
    """Create or update an Azure resource"""
    print(f"Creating/updating {resource_name}...")
    headers = get_headers(credential)
    resp = requests.put(uri, headers=headers, json=body)
    resp.raise_for_status()
    
    # Poll if async operation
    if resp.status_code == 201 and "Azure-AsyncOperation" in resp.headers:
        poll_async_operation(resp.headers["Azure-AsyncOperation"], credential)
    
    return resp.json()

# -------------------------------
# MAIN SCRIPT
# -------------------------------
try:
    credential = DefaultAzureCredential()
    
    # Get VHD size
    vhd_size = os.path.getsize(local_vhd_path)
    vhd_size_gb = vhd_size / (1024**3)
    print(f"VHD file size: {vhd_size_gb:.2f} GB ({vhd_size} bytes)")
    
    # -------------------------------
    # 1) CREATE RESOURCE GROUP (if needed)
    # -------------------------------
    print(f"\n=== Step 1: Ensuring Resource Group '{resource_group}' exists ===")
    rg_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourcegroups/{resource_group}?api-version=2021-04-01"
    )
    rg_body = {"location": location}
    create_or_update_resource(rg_uri, rg_body, credential, "Resource Group")
    
    # -------------------------------
    # 2) CREATE STORAGE ACCOUNT
    # -------------------------------
    print(f"\n=== Step 2: Creating Storage Account '{storage_account_name}' ===")
    storage_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Storage"
        f"/storageAccounts/{storage_account_name}?api-version=2023-01-01"
    )
    storage_body = {
        "location": location,
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2",
        "properties": {
            "allowBlobPublicAccess": False,
            "minimumTlsVersion": "TLS1_2"
        }
    }
    create_or_update_resource(storage_uri, storage_body, credential, "Storage Account")
    
    # Get storage account keys
    print("Getting storage account keys...")
    keys_uri = f"{storage_uri}/listKeys?api-version=2023-01-01"
    headers = get_headers(credential)
    keys_resp = requests.post(keys_uri, headers=headers)
    keys_resp.raise_for_status()
    storage_key = keys_resp.json()["keys"][0]["value"]
    
    # -------------------------------
    # 3) CREATE BLOB CONTAINER & UPLOAD VHD
    # -------------------------------
    print(f"\n=== Step 3: Uploading VHD to Storage Account ===")
    
    # Create blob service client
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=storage_key
    )
    
    # Create container
    print(f"Creating container '{container_name}'...")
    try:
        container_client = blob_service_client.create_container(container_name)
    except Exception as e:
        if "ContainerAlreadyExists" in str(e):
            print(f"Container '{container_name}' already exists.")
            container_client = blob_service_client.get_container_client(container_name)
        else:
            raise
    
    # Upload VHD as page blob
    blob_name = f"{new_vm_name}-os.vhd"
    print(f"Uploading {local_vhd_path} to blob '{blob_name}'...")
    print("This may take a while depending on disk size and network speed...")
    
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    # Upload with progress
    with open(local_vhd_path, "rb") as data:
        # For page blobs, size must be multiple of 512
        if vhd_size % 512 != 0:
            print("Warning: VHD size is not a multiple of 512 bytes")
        
        uploaded = 0
        blob_client.upload_blob(
            data,
            blob_type="PageBlob",
            max_concurrency=4,
            overwrite=True
        )
    
    vhd_url = blob_client.url
    print(f"✓ Upload complete!")
    print(f"VHD URL: {vhd_url}")
    
    # -------------------------------
    # 4) CREATE VIRTUAL NETWORK
    # -------------------------------
    print(f"\n=== Step 4: Creating Virtual Network '{vnet_name}' ===")
    vnet_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Network"
        f"/virtualNetworks/{vnet_name}?api-version=2023-05-01"
    )
    vnet_body = {
        "location": location,
        "properties": {
            "addressSpace": {
                "addressPrefixes": [vnet_address_prefix]
            },
            "subnets": [
                {
                    "name": subnet_name,
                    "properties": {
                        "addressPrefix": subnet_address_prefix
                    }
                }
            ]
        }
    }
    vnet_result = create_or_update_resource(vnet_uri, vnet_body, credential, "Virtual Network")
    subnet_id = vnet_result["properties"]["subnets"][0]["id"]
    
    # -------------------------------
    # 5) CREATE NETWORK SECURITY GROUP
    # -------------------------------
    print(f"\n=== Step 5: Creating Network Security Group '{nsg_name}' ===")
    nsg_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Network"
        f"/networkSecurityGroups/{nsg_name}?api-version=2023-05-01"
    )
    nsg_body = {
        "location": location,
        "properties": {
            "securityRules": [
                {
                    "name": "AllowSSH",
                    "properties": {
                        "protocol": "Tcp",
                        "sourcePortRange": "*",
                        "destinationPortRange": "22",
                        "sourceAddressPrefix": "*",
                        "destinationAddressPrefix": "*",
                        "access": "Allow",
                        "priority": 1000,
                        "direction": "Inbound"
                    }
                },
                {
                    "name": "AllowRDP",
                    "properties": {
                        "protocol": "Tcp",
                        "sourcePortRange": "*",
                        "destinationPortRange": "3389",
                        "sourceAddressPrefix": "*",
                        "destinationAddressPrefix": "*",
                        "access": "Allow",
                        "priority": 1001,
                        "direction": "Inbound"
                    }
                }
            ]
        }
    }
    nsg_result = create_or_update_resource(nsg_uri, nsg_body, credential, "Network Security Group")
    nsg_id = nsg_result["id"]
    
    # -------------------------------
    # 6) CREATE PUBLIC IP
    # -------------------------------
    print(f"\n=== Step 6: Creating Public IP '{public_ip_name}' ===")
    pip_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Network"
        f"/publicIPAddresses/{public_ip_name}?api-version=2023-05-01"
    )
    pip_body = {
        "location": location,
        "properties": {
            "publicIPAllocationMethod": "Dynamic"
        }
    }
    pip_result = create_or_update_resource(pip_uri, pip_body, credential, "Public IP")
    pip_id = pip_result["id"]
    
    # -------------------------------
    # 7) CREATE NETWORK INTERFACE
    # -------------------------------
    print(f"\n=== Step 7: Creating Network Interface '{nic_name}' ===")
    nic_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Network"
        f"/networkInterfaces/{nic_name}?api-version=2023-05-01"
    )
    nic_body = {
        "location": location,
        "properties": {
            "ipConfigurations": [
                {
                    "name": "ipconfig1",
                    "properties": {
                        "subnet": {"id": subnet_id},
                        "privateIPAllocationMethod": "Dynamic",
                        "publicIPAddress": {"id": pip_id}
                    }
                }
            ],
            "networkSecurityGroup": {"id": nsg_id}
        }
    }
    nic_result = create_or_update_resource(nic_uri, nic_body, credential, "Network Interface")
    nic_id = nic_result["id"]
    
    # -------------------------------
    # 8) CREATE MANAGED DISK FROM VHD
    # -------------------------------
    print(f"\n=== Step 8: Creating Managed Disk from VHD ===")
    disk_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Compute"
        f"/disks/{disk_name}?api-version=2023-04-02"
    )
    disk_body = {
        "location": location,
        "properties": {
            "creationData": {
                "createOption": "Import",
                "sourceUri": vhd_url,
                "storageAccountId": (
                    f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}"
                    f"/providers/Microsoft.Storage/storageAccounts/{storage_account_name}"
                )
            },
            "osType": "Linux"  # Change to "Windows" if needed
        }
    }
    disk_result = create_or_update_resource(disk_uri, disk_body, credential, "Managed Disk")
    disk_id = disk_result["id"]
    
    # -------------------------------
    # 9) CREATE VM FROM MANAGED DISK
    # -------------------------------
    print(f"\n=== Step 9: Creating VM '{new_vm_name}' ===")
    vm_uri = (
        f"https://management.azure.com/subscriptions/{subscription_id}"
        f"/resourceGroups/{resource_group}/providers/Microsoft.Compute"
        f"/virtualMachines/{new_vm_name}?api-version=2023-03-01"
    )
    vm_body = {
        "location": location,
        "properties": {
            "hardwareProfile": {
                "vmSize": vm_size
            },
            "storageProfile": {
                "osDisk": {
                    "osType": "Linux",  # Change to "Windows" if needed
                    "createOption": "Attach",
                    "managedDisk": {
                        "id": disk_id
                    }
                }
            },
            "networkProfile": {
                "networkInterfaces": [
                    {
                        "id": nic_id,
                        "properties": {
                            "primary": True
                        }
                    }
                ]
            }
        }
    }
    vm_result = create_or_update_resource(vm_uri, vm_body, credential, "Virtual Machine")
    
    print("\n" + "="*60)
    print("✓ ALL OPERATIONS COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nResource Group: {resource_group}")
    print(f"Storage Account: {storage_account_name}")
    print(f"Virtual Network: {vnet_name}")
    print(f"VM Name: {new_vm_name}")
    print(f"\nThe VM '{new_vm_name}' has been created and is starting up.")
    print("\nTo get the public IP address, run:")
    print(f"  az vm show -d -g {resource_group} -n {new_vm_name} --query publicIps -o tsv")
    
except requests.exceptions.RequestException as e:
    print(f"\n✗ HTTP Error: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Status: {e.response.status_code}")
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
