# GCP Configuration
vm_name = "your-vm-name"
project_id = "your-project-id"
zone = "europe-west1-b"  # Optional: specify zone, or None to search all
gcs_bucket = "vm-export-bucket"
download_path = "C:/temp"
credentials_path = "C:/path/to/service-account-key.json"
importdisktype= ("vmdk")
exportdisktype= "vmdk"
