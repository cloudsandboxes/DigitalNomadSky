aimport os
import subprocess
import sys
import json
# import custom config variables
import code/your-config/your-config



# -------------------------------
# 0) CONFIG / VARIABLES FILE
# -------------------------------
# Example JSON variables file:
# {
#     "source_platform": "azure",
#     "destination_platform": "aws",
#     "os_disk_path": "C:\\Temp\\osdisk.vhd",
#     "output_format": "vmdk",  # or "vhd"
#     "variables": {...}  # any cloud-specific variables
# }
variables_file = "variables.json"

with open(variables_file, "r") as f:
    config = json.load(f)

source_platform = config["source_platform"].lower()
destination_platform = config["destination_platform"].lower()
os_disk_path = config["os_disk_path"]
output_format = config["output_format"].lower()
vars_dict = config.get("variables", {})

# -------------------------------
# 1) INSTALL REQUIRED PYTHON PACKAGES
# -------------------------------
print("Installing required Python packages...")

def install_packages(packages):
    for pkg in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

platform_packages = {
    "azure": ["azure-identity", "azure-storage-blob", "requests"],
    "aws": ["boto3"],
    "gcp": ["google-cloud-storage"]
}

# Install packages for both source and destination
install_packages(platform_packages.get(source_platform, []))
install_packages(platform_packages.get(destination_platform, []))

# -------------------------------
# 2) DOWNLOAD AND INSTALL QEMU
# -------------------------------
# Only download if not present
qemu_path = r"C:\Program Files\qemu\qemu-img.exe" if os.name == "nt" else "/usr/bin/qemu-img"
if not os.path.exists(qemu_path):
    print("Downloading and installing QEMU...")
    if os.name == "nt":
        # Windows download link example (adjust version)
        qemu_installer = "https://qemu.weilnetz.de/w64/qemu-w64-setup-2023-07-26.exe"
        subprocess.run(["curl", "-L", "-o", "qemu-setup.exe", qemu_installer], check=True)
        subprocess.run(["start", "/wait", "qemu-setup.exe", "/S"], check=True)
    else:
        # Linux
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "qemu-utils"], check=True)
print("QEMU installed.")

# -------------------------------
# 3) EXECUTE SOURCE PLATFORM SCRIPT
# -------------------------------
source_script = f"{source_platform}version.py"
if os.path.exists(source_script):
    print(f"Executing source platform script: {source_script}")
    subprocess.run([sys.executable, source_script, variables_file], check=True)
else:
    raise FileNotFoundError(f"{source_script} not found!")

# -------------------------------
# 4) TRANSFORM OS DISK USING QEMU
# -------------------------------
output_disk_path = os.path.splitext(os_disk_path)[0] + f".{output_format}"
print(f"Transforming {os_disk_path} -> {output_disk_path} ...")
subprocess.run([qemu_path, "convert", "-O", output_format, os_disk_path, output_disk_path], check=True)
print(f"Disk conversion complete: {output_disk_path}")

# -------------------------------
# 5) EXECUTE DESTINATION PLATFORM SCRIPT
# -------------------------------
destination_script = f"{destination_platform}version.py"
if os.path.exists(destination_script):
    print(f"Executing destination platform script: {destination_script}")
    # Pass variables file and transformed disk path
    subprocess.run([sys.executable, destination_script, variables_file, output_disk_path], check=True)
else:
    raise FileNotFoundError(f"{destination_script} not found!")

print("Orchestration complete!")
