def upload_disk(glance, file_path, image_name, disk_format='qcow2', container_format='bare'):
    import os
    import time
    
    # Create image metadata
    image = glance.images.create(
        name=image_name,
        disk_format=disk_format,
        container_format=container_format,
        visibility='private'
    )
    
    # Upload in chunks
    chunk_size = 8192
    file_size = os.path.getsize(file_path)
    uploaded = 0
    
    with open(file_path, 'rb') as f:
        glance.images.upload(image.id, f)
    
    # Wait for image to become active (check every 5 seconds, max 30 minutes)
    for _ in range(360):
        img = glance.images.get(image.id)
        if img.status == 'active':
            return True, f"Image {image_name} uploaded (ID: {image.id})"
        elif img.status == 'error':
            return False, f"Upload failed"
        time.sleep(5)
    
    return False, f"Upload timeout"
