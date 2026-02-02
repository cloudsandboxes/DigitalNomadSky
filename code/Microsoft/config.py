#Parameters to find your VM. 
tenantid = "78ba35ee-470e-4a16-ba92-ad53510ad7f6"  # your tenant-id, this is used to find VMs.

#Parameters to upload your VM.
location = "westeurope"  # The VM will be created in this location.
destionationtenantid = "78ba35ee-470e-4a16-ba92-ad53510ad7f6" # the VM will be creaed in this tenant
subscription_id = "41aff5e1-41c9-4509-9fcb-d761d7f33740" # the VM will be created in this subscription
resource_group = "output" # the VM will be created in this resource group. 

storage_account_name = "compliceert20"   # a temp storage account to upload the disk file. 
container_name = "vhds"  # the temp container name to upload the disk file.  
