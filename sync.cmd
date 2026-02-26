@echo off
REM This script sets the BASE_DIR environment variable to the script's own directory,
REM then executes sync.exe.

REM The %~dp0 variable expands to the drive and path of the batch file.
set "BASE_DIR=%~dp0"

REM Execute the program.
"%~dp0\tools\sync.exe"
