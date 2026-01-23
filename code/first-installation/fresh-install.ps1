<#
===============================================================================
FUNCTION TEMPLATE — AI & VIBE CODER FRIENDLY
===============================================================================
WHAT THIS FUNCTION DOES
-----------------------
Installs Python, GIT and GITHUB repo on a new VM. 

Prompt:
I need a powershell script that downloads Python and git to a windows server and then clone an existing github repo.  This programs should be installed on a good location, so they could be used by the github code.

PARAMETERS (INPUT)
------------------
$RepoUrl = the URL of NomadSky code.
$CloneDirectory = location on server to install the source code. 

EXPECTED OUTPUT
---------------
- A server running the software. 

LOGGING POLICY
--------------

Remarks
--------------
PowerShell script to install Python, Git, and clone a GitHub repository
Run this script as Administrator

Troubleshoot actions
------------------
Check if python is installed:
Check if git is installed:
Check if repo is installed:
Check error logs:

===============================================================================
#>
param(
    [string]$GithubRepoUrl = "https://github.com/cloudsandboxes/nomadsky.git",
    [string]$CloneDirectory = "C:\Projects"
)

# Configuration
$PythonVersion = "3.12.1"
$PythonInstallPath = "C:\Program Files\Python312"
$GitInstallPath = "C:\Program Files\Git"
$TempDir = "$env:TEMP\DevToolsInstall"

# Create temp directory
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

Write-Host "=== Starting installation process ===" -ForegroundColor Green

# Function to add to PATH if not already present
function Add-ToPath {
    param([string]$PathToAdd)
    
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$PathToAdd*") {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$PathToAdd",
            "Machine"
        )
        Write-Host "Added $PathToAdd to system PATH" -ForegroundColor Yellow
    }
}

# Install Python
Write-Host "`n[1/3] Installing Python..." -ForegroundColor Cyan
$PythonUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-amd64.exe"
$PythonInstaller = "$TempDir\python-installer.exe"

try {
    Write-Host "Downloading Python $PythonVersion..."
    Invoke-WebRequest -Uri $PythonUrl -OutFile $PythonInstaller -UseBasicParsing
    
    Write-Host "Installing Python to $PythonInstallPath..."
    Start-Process -FilePath $PythonInstaller -ArgumentList @(
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1",
        "Include_test=0",
        "TargetDir=$PythonInstallPath"
    ) -Wait -NoNewWindow
    
    Add-ToPath "$PythonInstallPath"
    Add-ToPath "$PythonInstallPath\Scripts"
    
    Write-Host "Python installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Error installing Python: $_" -ForegroundColor Red
    exit 1
}

# Remove windows specific python settings
try {
    Write-Host "Remove windows default settings for Python"

    $aliases = @(
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe",
        "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.exe"
    )

    foreach ($alias in $aliases) {
        if (Test-Path $alias) {
            Remove-Item $alias -Force
            Write-Host "Removed alias: $alias"
        } else {
            Write-Host "Alias not found: $alias"
        }
    }
}catch {
    Write-Host "Error deinstalling windows settings for Python: $_" -ForegroundColor Red
    exit 1
}


# Install Git
# PowerShell script to download and install Git for Windows
# Run this script as Administrator

param(
    [string]$GitInstallPath = "C:\Program Files\Git"
)

# Configuration
$TempDir = "$env:TEMP\GitInstall"
$GitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
$GitInstaller = "$TempDir\git-installer.exe"

Write-Host "`n[2/3] Git Installation Script ..." -ForegroundColor Cyan

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "WARNING: This script should be run as Administrator for proper installation" -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit
    }
}

# Create temp directory
Write-Host "`nCreating temporary directory..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# Download Git
Write-Host "`nDownloading Git for Windows..." -ForegroundColor Cyan
Write-Host "URL: $GitUrl"
Write-Host "Downloading to: $GitInstaller"

try {
    Invoke-WebRequest -Uri $GitUrl -OutFile $GitInstaller -UseBasicParsing
    Write-Host "Download completed successfully!" -ForegroundColor Green
    
    # Verify download
    if (Test-Path $GitInstaller) {
        $fileSize = (Get-Item $GitInstaller).Length / 1MB
        Write-Host "Downloaded file size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
    }
} catch {
    Write-Host "Error downloading Git: $_" -ForegroundColor Red
    exit 1
}

# Install Git
Write-Host "`nInstalling Git..." -ForegroundColor Cyan
Write-Host "Installation path: $GitInstallPath"

try {
    $installArgs = @(
        "/VERYSILENT",
        "/NORESTART",
        "/NOCANCEL",
        "/SP-",
        "/CLOSEAPPLICATIONS",
        "/RESTARTAPPLICATIONS",
        "/DIR=$GitInstallPath",
        "/COMPONENTS=icons,ext\shellhere,assoc,assoc_sh"
    )
    
    Write-Host "Starting installation process..."
    $process = Start-Process -FilePath $GitInstaller -ArgumentList $installArgs -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Host "Git installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Installation completed with exit code: $($process.ExitCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Error installing Git: $_" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

if (Test-Path "C:\Program\git-cmd.exe") {
    Write-Host "Git executable found at: C:\Program\git-cmd.exe" -ForegroundColor Green
    
    # Add to PATH
    Write-Host "`nAdding Git to system PATH..." -ForegroundColor Cyan
    try {
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
        $gitCmdPath = "C:\Program\"
        
        if ($currentPath -notlike "*$gitCmdPath*") {
            [Environment]::SetEnvironmentVariable(
                "Path",
                "$currentPath;$gitCmdPath",
                "Machine"
            )
            Write-Host "Added $gitCmdPath to system PATH" -ForegroundColor Green
            
            # Refresh PATH for current session
            $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine")
        } else {
            Write-Host "Git is already in system PATH" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Could not add Git to PATH automatically. You may need to add it manually: $gitCmdPath" -ForegroundColor Yellow
    }
    
    # Test Git
    Write-Host "`nTesting Git installation..." -ForegroundColor Cyan
    try {
        $gitVersion = git --version
        Write-Host "Git version: $gitVersion" -ForegroundColor Green
    } catch {
        Write-Host "Git installed but could not get version. Try restarting PowerShell." -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: Git executable not found at expected location!" -ForegroundColor Red
    Write-Host "Expected location: C:\Program\git-cmd.exe" -ForegroundColor Red
    Write-Host "Please check if Git was installed to a different location." -ForegroundColor Yellow
}

# Cleanup
Write-Host "`nCleaning up temporary files..." -ForegroundColor Cyan
try {
    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Cleanup completed" -ForegroundColor Green
} catch {
    Write-Host "Could not remove temporary directory: $TempDir" -ForegroundColor Yellow
}

Write-Host "`n=== Installation Complete ===" -ForegroundColor Green
Write-Host "Git installation path: C:\Program\git-cmd.exe"
Write-Host "`nNote: You may need to restart your PowerShell session for PATH changes to take effect." -ForegroundColor Yellow
Write-Host "To verify, open a new PowerShell window and run: git --version" -ForegroundColor Cyan








# Clone GitHub repository
Write-Host "`n[3/3] Cloning GitHub repository..." -ForegroundColor Cyan
# PowerShell script to clone a GitHub repository

# Extract repository name from URL
Write-Host "`nParsing repository URL..." -ForegroundColor Cyan
$repoName = ($GithubRepoUrl -split '/')[-1] -replace '\.git$', ''
Write-Host "Repository name: $repoName" -ForegroundColor Gray

# Create clone directory if it doesn't exist
if (-not (Test-Path $CloneDirectory)) {
    Write-Host "`nCreating directory: $CloneDirectory" -ForegroundColor Cyan
    try {
        New-Item -ItemType Directory -Force -Path $CloneDirectory | Out-Null
        Write-Host "Directory created successfully" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Could not create directory: $_" -ForegroundColor Red
        echo $"help"
    }
}

# Full path where repo will be cloned
$repoPath = Join-Path $CloneDirectory $repoName

# Check if repository already exists
if (Test-Path $repoPath) {
    Write-Host "`nRepository already exists at: $repoPath" -ForegroundColor Yellow
    $choice = Read-Host "Do you want to (p)ull latest changes, (d)elete and re-clone, or (c)ancel? [p/d/c]"
    
    switch ($choice.ToLower()) {
        'p' {
            Write-Host "`nPulling latest changes..." -ForegroundColor Cyan
            Set-Location $repoPath
            try {
                & $gitExe pull
                Write-Host "`nRepository updated successfully!" -ForegroundColor Green
                Write-Host "Location: $repoPath" -ForegroundColor Cyan
                exit 0
            } catch {
                Write-Host "ERROR: Failed to pull changes: $_" -ForegroundColor Red
                exit 0
            }
        }
        'd' {
            Write-Host "`nDeleting existing repository..." -ForegroundColor Yellow
            try {
                Remove-Item -Path $repoPath -Recurse -Force
                Write-Host "Deleted successfully" -ForegroundColor Green
            } catch {
                Write-Host "ERROR: Could not delete existing repository: $_" -ForegroundColor Red
                exit 0
            }
        }
        default {
            Write-Host "Operation cancelled" -ForegroundColor Yellow
            exit 0
        }
    }
}

# Clone the repository
Write-Host "`nCloning repository..." -ForegroundColor Cyan
Write-Host "From: $GitHubRepoUrl" -ForegroundColor Gray
Write-Host "To: $repoPath" -ForegroundColor Gray

try {
    Set-Location $CloneDirectory
    
    # Execute git clone
    git clone $GithubRepoUrl $repoPath
    # & $gitExe clone $GithubRepoUrl 2>&1 | ForEach-Object {
    #    Write-Host $_ -ForegroundColor Gray
    # }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=== Clone Successful ===" -ForegroundColor Green
        Write-Host "Repository cloned to: $repoPath" -ForegroundColor Cyan
        
        # Show repository info
        if (Test-Path $repoPath) {
            Set-Location $repoPath
            Write-Host "`nRepository information:" -ForegroundColor Cyan
            # & $gitExe remote -v
            # Write-Host ""
            # & $gitExe branch
        }
    } else {
        Write-Host "`nERROR: Git clone failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Failed to clone repository: $_" -ForegroundColor Red
    # exit 0
}

Write-Host "`nDone!" -ForegroundColor Green


# Cleanup
Write-Host "`nCleaning up temporary files..." -ForegroundColor Cyan
Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue

# Verify installations
Write-Host "`n=== Installation Summary ===" -ForegroundColor Green
Write-Host "Python version:" -NoNewline
& "$PythonInstallPath\python.exe" --version
Write-Host "Repository location: $CloneDirectory\$RepoName"

Write-Host "`nInstallation complete! Please restart your PowerShell session for PATH changes to take full effect." -ForegroundColor Green
