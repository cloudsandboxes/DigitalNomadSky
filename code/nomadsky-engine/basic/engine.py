import os
import subprocess
import sys

# -------------------------------
# 1) DOWNLOAD AND INSTALL QEMU
# -------------------------------
# Only download if not present
qemu_path = r"C:\Temp\qemu-w64-setup-20251224.exe"
if not os.path.exists(qemu_path):
    print("Downloading and installing QEMU...")
    if os.name == "nt":
        # Windows download link example (adjust version)
        # Option 2: Download latest from official source
        download_path = "C:/temp/qemu-setup.exe"
        qemu_installer = "https://qemu.weilnetz.de/w64/qemu-w64-setup-2051224.exe"
        subprocess.run(["curl", "-L", "-o", download_path, qemu_installer], check=True)
        print ("i work tilll here")
        startpath= r"C:\Temp\qemu-w64-setup-20251224.exe"
        subprocess.run(["start", "/wait", startpath, "/S"], check=True)
        #qemu_installer = "https://qemu.weilnetz.de/w64/qemu-w64-setup-2023-07-26.exe"
        #subprocess.run(["curl", "-L", "-o", "qemu-setup.exe", qemu_installer], check=True)
        #subprocess.run(["start", "/wait", "qemu-setup.exe", "/S"], check=True)
    else:
        # Linux
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "qemu-utils"], check=True)
print("QEMU installed.")
