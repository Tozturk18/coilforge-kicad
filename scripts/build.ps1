# Build script for Windows (PowerShell)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path build | Out-Null
Set-Location build
cmake ..
cmake --build .
