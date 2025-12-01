# -------------------------------
# VARIABLES
# -------------------------------
$projectId      = "<GCP_PROJECT_ID>"
$zone           = "<VM_ZONE>"             # e.g. "us-central1-a"
$instanceName   = "<INSTANCE_NAME>"
$bucketName     = "<GCS_BUCKET_NAME>"
$outputVhdPath  = "C:\Temp\bootdisk.vhd"
$imageName      = "$instanceName-export-$(Get-Date -Format yyyyMMddHHmmss)"

# -------------------------------
# 0) GET AUTH TOKEN
# -------------------------------
# Assumes gcloud SDK is installed and logged in
$token = gcloud auth print-access-token
$headers = @{ Authorization = "Bearer $token" }

# -------------------------------
# 1) STOP THE VM
# -------------------------------
$stopUri = "https://compute.googleapis.com/compute/v1/projects/$projectId/zones/$zone/instances/$instanceName/stop"
Write-Host "Stopping VM..."
Invoke-RestMethod -Method Post -Uri $stopUri -Headers $headers

Start-Sleep -Seconds 20

# -------------------------------
# 2) CREATE IMAGE FROM BOOT DISK
# -------------------------------
$diskName = $instanceName  # assuming boot disk has same name
$createImageUri = "https://compute.googleapis.com/compute/v1/projects/$projectId/global/images"

$body = @{
    name = $imageName
    sourceDisk = "projects/$projectId/zones/$zone/disks/$diskName"
} | ConvertTo-Json -Depth 10

Write-Host "Creating image from boot disk..."
Invoke-RestMethod -Method Post -Uri $createImageUri -Headers $headers -Body $body -ContentType "application/json"

# Wait a bit for image to be ready
Start-Sleep -Seconds 30

# -------------------------------
# 3) EXPORT IMAGE TO GCS AS VHD
# -------------------------------
$exportUri = "https://compute.googleapis.com/compute/v1/projects/$projectId/global/images/$imageName/export"

$exportBody = @{
    destinationUri = "gs://$bucketName/$imageName.vhd"
    exportFormat = "vhd"
} | ConvertTo-Json -Depth 10

Write-Host "Exporting image to GCS..."
Invoke-RestMethod -Method Post -Uri $exportUri -Headers $headers -Body $exportBody -ContentType "application/json"

# Wait for export to finish (can take minutes)
Write-Host "Waiting 2–5 minutes for export to complete..."
Start-Sleep -Seconds 300

# -------------------------------
# 4) DOWNLOAD VHD FROM GCS
# -------------------------------
Write-Host "Downloading VHD from GCS..."
gsutil cp "gs://$bucketName/$imageName.vhd" $outputVhdPath

Write-Host "Download complete: $outputVhdPath"
