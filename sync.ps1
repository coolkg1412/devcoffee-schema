# This script sets the BASE_DIR environment variable to the script's own directory,
# then executes sync.exe.

# Get the directory where this script is located.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Set the BASE_DIR environment variable for the process.
$env:BASE_DIR = $ScriptDir

# Construct the full path to the executable.
$ExePath = Join-Path -Path $ScriptDir -ChildPath "tools/sync.exe"

# Execute the program.
& $ExePath
