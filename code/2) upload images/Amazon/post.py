import boto3
import os
from boto3.s3.transfer import TransferConfig
import time

# -------------------------------
# VARIABLES
# -------------------------------
region_name = "eu-west-1"
bucket_name = "<YOUR_S3_BUCKET>"
vmdk_local_path = r"C:\Temp\osdisk.vmdk"
vmdk_s3_key = "ec2-uploads/osdisk.vmdk"
role_name = "vmimport"  # Pre-created IAM role
ami_name = "Imported-AMI"
instance_type = "t2.micro"
key_name = "<YOUR_KEY_PAIR>"  # SSH key for Linux or leave for Windows

# -------------------------------
# 1) CREATE S3 BUCKET (if needed)
# -------------------------------
s3 = boto3.client("s3", region_name=region_name)
existing_buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]

if bucket_name not in existing_buckets:
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": region_name})
    print(f"S3 bucket {bucket_name} created.")
else:
    print(f"S3 bucket {bucket_name} exists.")

# -------------------------------
# 2) UPLOAD VMDK TO S3 (chunked)
# -------------------------------
config = TransferConfig(multipart_threshold=100 * 1024 * 1024, max_concurrency=4)
print(f"Uploading {vmdk_local_path} to s3://{bucket_name}/{vmdk_s3_key} ...")
s3.upload_file(vmdk_local_path, bucket_name, vmdk_s3_key, Config=config)
print("Upload complete.")

# -------------------------------
# 3) CREATE IMPORT TASK TO AMI
# -------------------------------
ec2 = boto3.client("ec2", region_name=region_name)
import_task = ec2.import_image(
    Description="Imported VM",
    DiskContainers=[
        {
            "Description": "OS Disk",
            "Format": "vmdk",
            "UserBucket": {"S3Bucket": bucket_name, "S3Key": vmdk_s3_key}
        }
    ],
    RoleName=role_name
)
import_task_id = import_task["ImportTaskId"]
print(f"Import task started: {import_task_id}")

# Wait for import task to complete
while True:
    task_status = ec2.describe_import_image_tasks(ImportTaskIds=[import_task_id])
    status = task_status["ImportImageTasks"][0]["Status"]
    print(f"Import status: {status}")
    if status == "completed":
        ami_id = task_status["ImportImageTasks"][0]["ImageId"]
        break
    elif status == "deleted" or status == "deleting" or status == "failed":
        raise Exception("Import task failed")
    time.sleep(30)

print(f"AMI created: {ami_id}")

# -------------------------------
# 4) LAUNCH EC2 INSTANCE FROM AMI
# -------------------------------
instance = ec2.run_instances(
    ImageId=ami_id,
    InstanceType=instance_type,
    KeyName=key_name,
    MinCount=1,
    MaxCount=1
)
instance_id = instance["Instances"][0]["InstanceId"]
print(f"EC2 instance launched: {instance_id}")

