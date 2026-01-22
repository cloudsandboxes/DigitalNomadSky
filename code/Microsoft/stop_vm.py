# -------------------------------
# Stop the VM in Azure with the given name. Input variables is the VM name to stop, existing parameters from shared_data. 
# Other input variables are read from config.py
# The output is non. The VM just stopped.
# When running this script for testing, fill in parameters: for resource_id is the vm to stop., vmname = vmname, source is azure, destination not needed. 
# -------------------------------


def stop_vm(shared_data):
        import sys
        import json
        sys.path.append(r"C:/projects/nomadsky/code/Microsoft")
        from azure.identity import InteractiveBrowserCredential
        from azure.mgmt.compute import ComputeManagementClient
        # Get arguments
        source = sys.argv[1]
        destination = sys.argv[2]
        vmname = sys.argv[3].lower()
        import config
        shared_data_json = sys.argv[4]  # 4th argument
        shared_data = json.loads(shared_data_json)
        # Extract specific value
        resource_id = shared_data.get('resource_id', '')


    

        # Parse subscription_id, resource_group, and vm_name from resource ID
        parts = resource_id.strip("/").split("/")
        try:
            subscription_id = parts[1]
            resource_group = parts[3]
        except IndexError:
            raise Exception(f" Invalid resource ID format: '{resource_id}' ")
            return

        # Authenticate interactively
        tenant_id = config.tenantid
        credential = InteractiveBrowserCredential(tenant_id=tenant_id)

        # Create compute client
        compute_client = ComputeManagementClient(credential, subscription_id)

        # Deallocate the VM
        # print(f"Deallocating VM '{vmname}' in resource group '{resource_group}'...")
        async_vm_deallocate = compute_client.virtual_machines.begin_deallocate(resource_group, vmname)
        async_vm_deallocate.wait()  # Wait until deallocation is complete
        # print(f"VM '{vmname}' has been deallocated successfully!")

        result = {
          'message': f"VM '{vmname}' has been deallocated successfully!",
          'resource_id': vm_resource_id
        }
        
        return json.dumps(result)
