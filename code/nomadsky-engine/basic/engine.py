import os
import subprocess
import sys

# -------------------------------
# 1) DOWNLOAD AND INSTALL QEMU
# -------------------------------
# Only download if not present
qemu_path = r"C:\Program Files\qemu\qemu-img.exe"
if not os.path.exists(qemu_path):
    print("Downloading and installing QEMU...")
    if os.name == "nt":
        # Windows download link example (adjust version)
        download_path = "C:/path/to/your/folder/qemu-setup.exe"
        qemu_installer = "https://qemu.weilnetz.de/w64/qemu-w64-setup-2023-07-26.exe"
        subprocess.run(["curl", "-L", "-o", download_path, qemu_installer], check=True)
        subprocess.run(["start", "/wait", download_path, "/S"], check=True)
        #qemu_installer = "https://qemu.weilnetz.de/w64/qemu-w64-setup-2023-07-26.exe"
        #subprocess.run(["curl", "-L", "-o", "qemu-setup.exe", qemu_installer], check=True)
        #subprocess.run(["start", "/wait", "qemu-setup.exe", "/S"], check=True)
    else:
        # Linux
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "qemu-utils"], check=True)
print("QEMU installed.")
