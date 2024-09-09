# Function to get the extension directories for Chrome
function Get-ChromeExtensions {
    $chromeExtensionsPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Extensions"
    
    if (Test-Path $chromeExtensionsPath) {
        return Get-ChildItem -Path $chromeExtensionsPath | Where-Object { $_.PSIsContainer }
    } else {
        Write-Output "Chrome extensions directory not found."
        return @()
    }
}

# Function to get the extension directories for Edge
function Get-EdgeExtensions {
    $edgeExtensionsPath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Extensions"
    
    if (Test-Path $edgeExtensionsPath) {
        return Get-ChildItem -Path $edgeExtensionsPath | Where-Object { $_.PSIsContainer }
    } else {
        Write-Output "Edge extensions directory not found."
        return @()
    }
}

# Get Chrome and Edge extension IDs
$chromeExtensions = Get-ChromeExtensions
$edgeExtensions = Get-EdgeExtensions

Write-Output "Combined Extension IDs for Chrome and Edge:"

# Combine the extension IDs from both browsers
$allExtensions = $chromeExtensions + $edgeExtensions

foreach ($extension in $allExtensions) {
    Write-Output $extension.Name
}
