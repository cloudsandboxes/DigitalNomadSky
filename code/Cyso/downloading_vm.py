def export_os_disk(nova, vm_name, image_name=None):
    # Find VM by name
    servers = nova.servers.list(search_opts={'name': vm_name})
    if not servers:
        return False, "VM not found"
    
    server = servers[0]
    
    # Create snapshot/image of the VM
    if not image_name:
        image_name = f"{vm_name}_snapshot_{int(__import__('time').time())}"
    
    image_id = server.create_image(image_name)
    return True, f"Creating image {image_name} (ID: {image_id})"
