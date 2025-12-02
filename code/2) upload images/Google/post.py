"""
Before running, install dependencies:

1) Google Cloud SDK (for gcloud CLI)
   - https://cloud.google.com/sdk/docs/install

2) Python packages
   pip install google-cloud-storage
"""

import os
import subprocess
from google.cloud import storage

# -------------------------------
# VARIABLES
# -------------------------------
project_id = "<PROJECT_ID>"
zone = "europe-west1-b"
instance_name = "<NEW_VM_NAME>"
disk_local_path = r"C:\Temp\osdisk.vmdk"  # VMDK or VHD
bucket_name = "<GCS_BUCKET>"
gcs_object_name = f"osdisk/{os.path.basename(disk_local_path)}"
machine_type = "e2-medium"

# -------------------------------
# 1) UPLOAD VMDK/VHD TO GCS
# -------------------------------
# Set path to service account JSON key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"<PATH_TO_SERVICE_ACCOUNT_JSON>"

storage_client = storage.Client(project=project_id)
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(gcs_object_name)

print(f"Uploading {disk_local_path} to gs://{bucket_name}/{gcs_object_name} ...")
blob.chunk_size = 8 * 1024 * 1024  # 8 MB chunked upload
blob.upload_from_filename(disk_local_path)
print("Upload complete.")

# -------------------------------
# 2) CREATE CUSTOM IMAGE FROM GCS OBJECT
# -------------------------------
image_name = f"{instance_name}-image"
print(f"Creating custom image {image_name} from GCS object ...")

subprocess.run([
    "gcloud", "compute", "images", "create", image_name,
    "--source-uri", f"gs://{bucket_name}/{gcs_object_name}",
    "--project", project_id,
    "--quiet"
], check=True)
print(f"Custom image {image_name} created.")

# -------------------------------
# 3) CREATE VM INSTANCE FROM IMAGE
# -------------------------------
print(f"Creating V
