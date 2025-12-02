import time
import subprocess
import os
from google.cloud import compute_v1, storage

# -------------------------------
# VARIABLES
# -------------------------------
project_id = "<PROJECT_ID>"
zone = "<ZONE>"  # e.g., "europe-west1-b"
instance_name = "<INSTANCE_NAME>"
output_file = r"C:\Temp\gcp_disk.vmdk"  # or .vhd
bucket_name = "<GCS_BUCKET>"

# -------------------------------
# 1) STOP THE VM
# -------------------------------
instance_client = compute_v1.InstancesClient()
print("Stopping GCP VM...")
operation = instance_client.stop(project=project_id, zone=zone, instance=instance_name)
operation.result()  # wait for completion
print("VM stopped.")

# -------------------------------
# 2) GET BOOT DISK NAME
# -------------------------------
instance = instance_client.get(project=project_id, zone=zone, instance=instance_name)
boot_disk_name = instance.disks[0].initialize_params.source_image or instance.disks[0].source.split("/")[-1]
print(f"Boot disk name: {boot_disk_name}")

# -------------------------------
# 3) CREATE SNAPSHOT
# -------------------------------
snapshots_client = compute_v1.SnapshotsClient()
snapshot_name = f"{boot_disk_name}-snapshot"
print(f"Creating snapshot: {snapshot_name}...")
snap_op = snapshots_client.insert(
    project=project_id,
    snapshot_resource=compute_v1.Snapshot(name=snapshot_name, source_disk=f"projects/{project_id}/zones/{zone}/disks/{boot_disk_name}")
)
snap_op.result()
print("Snapshot created.")

# -------------------------------
# 4) EXPORT SNAPSHOT TO GCS
# -------------------------------
# Use gcloud CLI for export, as API doesn't provide direct disk format conversion
export_format = "vmdk"  # or "vhd"
gcs_path = f"gs://{bucket_name}/{s
