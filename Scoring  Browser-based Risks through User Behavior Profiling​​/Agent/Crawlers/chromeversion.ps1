# Function to find the Edge executable
function Find-EdgeExecutable {
    $paths = @(
        "$env:PROGRAMFILES\Microsoft\Edge\Application\msedge.exe",
        "$env:PROGRAMFILES(X86)\Microsoft\Edge\Application\msedge.exe",
        "$env:LOCALAPPDATA\Microsoft\Edge\Application\msedge.exe",
        "$env:PROGRAMFILES\Microsoft\Edge Beta\Application\msedge.exe",
        "$env:PROGRAMFILES(X86)\Microsoft\Edge Beta\Application\msedge.exe",
        "$env:PROGRAMFILES\Microsoft\Edge Dev\Application\msedge.exe",
        "$env:PROGRAMFILES(X86)\Microsoft\Edge Dev\Application\msedge.exe"
    )

    foreach ($path in $paths) {
        if (Test-Path $path) {
            return $path
        }
    }

    Write-Output "Edge executable not found."
    exit
}

# Function to get the Edge version
function Get-EdgeVersion {
    param (
        $edgeExecutable
    )

    # Get the version information from the executable
    $versionInfo = (Get-Item $edgeExecutable).VersionInfo
    return $versionInfo.ProductVersion
}

# Find the Edge executable
$edgeExecutable = Find-EdgeExecutable

# Get the Edge version
$edgeVersion = Get-EdgeVersion -edgeExecutable $edgeExecutable

# Output the Edge version
Write-Output "Microsoft Edge version: $edgeVersion"
