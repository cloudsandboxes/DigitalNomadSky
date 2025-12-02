import boto3
import time
import os

# -------------------------------
# VARIABLES
# -------------------------------
region_name = "eu-west-1"
instance_id = "<INSTANCE_ID>"
output_file = r"C:\Temp\ec2_disk.vmdk"  # or .vhdx
s3_bucket = "<YOUR_S3_BUCKET>"
s3_prefix = "ec2-exports/"

# -------------------------------
# SETUP
# -------------------------------
ec2 = boto3.client("ec2", region_name=region_name)
s3 = boto3.client("s3", region_name=region_name)
iam = boto3.client("iam", region_name=region_name)

# -------------------------------
# 1) STOP THE INSTANCE
# -------------------------------
print("Stopping EC2 instance...")
ec2.stop_instances(InstanceIds=[instance_id])
waiter = ec2.get_waiter('instance_stopped')
waiter.wait(InstanceIds=[instance_id])
print("Instance stopped.")

# -------------------------------
# 2) GET ROOT VOLUME
# -------------------------------
desc = ec2.describe_instances(InstanceIds=[instance_id])
root_device_name = desc["Reservations"][0]["Instances"][0]["RootDeviceName"]
root_volume_id = None
for mapping in desc["Reservations"][0]["Instances"][0]["BlockDeviceMappings"]:
    if mapping["DeviceName"] == root_device_name:
        root_volume_id = mapping["Ebs"]["VolumeId"]

print(f"Root volume ID: {root_volume_id}")

# -------------------------------
# 3) CREATE SNAPSHOT
# -------------------------------
snapshot = ec2.create_snapshot(
    VolumeId=root_volume_id,
    Description=f"Snapshot of {root_volume_id} for export"
)
snapshot_id = snapshot["SnapshotId"]
print(f"Snapshot created: {snapshot_id}")

# Wait for snapshot completion
print("Waiting for snapshot to complete...")
snapshot_waiter = ec2.get_waiter('snapshot_completed')
snapshot_waiter.wait(SnapshotIds=[snapshot_id])
print("Snapshot completed.")

# -------------------------------
# 4) EXPORT SNAPSHOT TO S3 (VMDK or VHDX)
# -------------------------------
# VM Import/Export requires a role with permission
