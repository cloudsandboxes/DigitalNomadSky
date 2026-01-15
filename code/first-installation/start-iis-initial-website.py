#!/usr/bin/env python3
"""
Python script to upload HTML files to IIS from a fixed folder location
Usage: python start-iis-initial-website.py --source "C:\path\to\your\folder" --file "index.html"
"""

import os
import shutil
import sys
import ctypes
import argparse
from pathlib import Path

def is_admin():
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_iis_root():
    """Find the IIS wwwroot directory"""
    possible_paths = [
        r"C:\inetpub\wwwroot",
        r"C:\inetpub\wwwroot\\",
        os.path.join(os.environ.get('SystemDrive', 'C:'), r"\inetpub\wwwroot")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def normalize_path(path):
    """Normalize and resolve the path"""
    # Remove quotes and strip whitespace
    path = path.strip().strip('"').strip("'")
    
    # Expand environment variables
    path = os.path.expandvars(path)
    
    # Convert to absolute path
    path = os.path.abspath(path)
    
    return path

def find_file_in_folder(folder_path, filename):
    """
    Search for a file in the folder and its subdirectories
    Returns the full path to the file if found
    """
    folder_path = normalize_path(folder_path)
    
    print(f"\nSearching for '{filename}' in: {folder_path}")
    
    # First check if the file is directly in the folder
    direct_path = os.path.join(folder_path, filename)
    if os.path.isfile(direct_path):
        print(f"✓ Found file at: {direct_path}")
        return direct_path
    
    # Search in subdirectories
    for root, dirs, files in os.walk(folder_path):
        if filename in files:
            full_path = os.path.join(root, filename)
            print(f"✓ Found file at: {full_path}")
            return full_path
    
    return None

def upload_file(source_file, iis_root, target_name=None):
    """Upload a single file to IIS wwwroot"""
    if not os.path.exists(source_file):
        print(f"✗ Error: Source file not found: {source_file}")
        return False
    
    # Use original filename if no target name specified
    if target_name is None:
        target_name = os.path.basename(source_file)
    
    target_path = os.path.join(iis_root, target_name)
    
    try:
        print(f"\nCopying file...")
        print(f"  From: {source_file}")
        print(f"  To:   {target_path}")
        
        shutil.copy2(source_file, target_path)
        
        file_size = os.path.getsize(target_path)
        print(f"\n✓ Successfully uploaded: {target_name}")
        print(f"  Size: {file_size} bytes")
        return True
    except PermissionError:
        print(f"✗ Permission denied. Make sure you're running as Administrator")
        return False
    except Exception as e:
        print(f"✗ Error uploading file: {e}")
        return False

def upload_directory(source_dir, iis_root, subfolder=None):
    """Upload entire directory to IIS wwwroot"""
    source_dir = normalize_path(source_dir)
    
    if not os.path.exists(source_dir):
        print(f"✗ Error: Source directory not found: {source_dir}")
        return False
    
    # Determine target directory
    if subfolder:
        target_dir = os.path.join(iis_root, subfolder)
    else:
        target_dir = iis_root
    
    try:
        # Create subfolder if needed
        if subfolder and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"✓ Created directory: {target_dir}")
        
        # Copy all files
        file_count = 0
        for root, dirs, files in os.walk(source_dir):
            # Calculate relative path
            rel_path = os.path.relpath(root, source_dir)
            
            # Create corresponding directory in target
            if rel_path != ".":
                target_subdir = os.path.join(target_dir, rel_path)
            else:
                target_subdir = target_dir
            
            if not os.path.exists(target_subdir):
                os.makedirs(target_subdir)
            
            # Copy files
            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_subdir, file)
                
                shutil.copy2(source_file, target_file)
                rel_target = os.path.relpath(target_file, iis_root)
                print(f"  ✓ {file} -> {rel_target}")
                file_count += 1
        
        print(f"\n✓ Successfully uploaded {file_count} file(s)")
        return True
        
    except PermissionError:
        print(f"✗ Permission denied. Make sure you're running as Administrator")
        return False
    except Exception as e:
        print(f"✗ Error uploading directory: {e}")
        return False

def list_iis_files(iis_root):
    """List files currently in IIS wwwroot"""
    print(f"\nFiles in IIS root ({iis_root}):")
    print("="*50)
    
    try:
        items = os.listdir(iis_root)
        if not items:
            print("  (empty)")
        else:
            for item in sorted(items):
                item_path = os.path.join(iis_root, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    print(f"  📄 {item} ({size:,} bytes)")
                else:
                    print(f"  📁 {item}/")
    except Exception as e:
        print(f"✗ Error listing files: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Upload HTML files to IIS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload a specific file
  python upload_to_iis.py --source "C:\\Projects\\myapp" --file "index.html"
  
  # Upload entire directory
  python upload_to_iis.py --source "C:\\Projects\\myapp" --all
  
  # Upload entire directory to a subfolder
  python upload_to_iis.py --source "C:\\Projects\\myapp" --all --subfolder "myapp"
        """
    )
    
    parser.add_argument('--source', required=True, help='Source folder path (e.g., "C:\\Projects\\myapp")')
    parser.add_argument('--file', help='Specific filename to upload (e.g., "index.html")')
    parser.add_argument('--all', action='store_true', help='Upload entire directory')
    parser.add_argument('--subfolder', help='Subfolder name in IIS (optional)')
    parser.add_argument('--rename', help='Rename the file when uploading (optional)')
    
    args = parser.parse_args()
    
    print("="*50)
    print("IIS File Upload Script")
    print("="*50)
    
    # Check if running as administrator
    if not is_admin():
        print("\n✗ ERROR: This script must be run as Administrator!")
        print("Please right-click Python/PowerShell and select 'Run as Administrator'")
        sys.exit(1)
    
    print("✓ Running with Administrator privileges")
    
    # Find IIS root directory
    iis_root = find_iis_root()
    if not iis_root:
        print("\n✗ ERROR: Could not find IIS wwwroot directory!")
        print("Expected location: C:\\inetpub\\wwwroot")
        sys.exit(1)
    
    print(f"✓ Found IIS root: {iis_root}")
    
    # Validate source folder
    source_folder = normalize_path(args.source)
    if not os.path.exists(source_folder):
        print(f"\n✗ ERROR: Source folder not found: {source_folder}")
        sys.exit(1)
    
    print(f"✓ Source folder: {source_folder}")
    
    # Show current IIS files
    list_iis_files(iis_root)
    
    print("\n" + "="*50)
    print("Starting upload...")
    print("="*50)
    
    # Upload based on mode
    if args.all:
        # Upload entire directory
        success = upload_directory(source_folder, iis_root, args.subfolder)
        
        if success:
            if args.subfolder:
                print(f"\n✓ Directory uploaded successfully!")
                print(f"📍 Access at: http://localhost/{args.subfolder}/")
            else:
                print(f"\n✓ Directory uploaded successfully!")
                print(f"📍 Access at: http://localhost/")
    
    elif args.file:
        # Upload specific file
        source_file = find_file_in_folder(source_folder, args.file)
        
        if not source_file:
            print(f"\n✗ ERROR: File '{args.file}' not found in {source_folder}")
            print("\nSearched in all subdirectories.")
            sys.exit(1)
        
        target_name = args.rename if args.rename else args.file
        success = upload_file(source_file, iis_root, target_name)
        
        if success:
            print(f"\n✓ File uploaded successfully!")
            print(f"📍 Access at: http://localhost/{target_name}")
    
    else:
        print("\n✗ ERROR: You must specify either --file or --all")
        parser.print_help()
        sys.exit(1)
    
    # Show updated file list
    print("\n" + "="*50)
    list_iis_files(iis_root)
    
    print("\n" + "="*50)
    print("Upload completed!")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1
