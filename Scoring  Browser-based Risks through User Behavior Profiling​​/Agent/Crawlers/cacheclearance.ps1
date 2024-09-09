# Define the path to Chrome's cache folder
$cachePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"

# Check if the cache folder exists
if (-Not (Test-Path $cachePath)) {
    Write-Output "Chrome Cache folder not found."
    exit
}

# Get the size of the cache folder
$cacheSize = (Get-ChildItem -Recurse -Force -Path $cachePath | Measure-Object -Property Length -Sum).Sum
$cacheSizeMB = [math]::Round($cacheSize / 1MB, 2)

# Get the last modified date of files in the cache folder
$lastModified = Get-ChildItem -Recurse -Force -Path $cachePath | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Select-Object -ExpandProperty LastWriteTime

# Output the cache size and last modified time
Write-Output "Cache folder size: $cacheSizeMB MB"
Write-Output "Last modified time of cache files: $lastModified"

# Estimate cache clearing frequency
$daysSinceLastModification = (Get-Date) - $lastModified
Write-Output "Days since last cache modification: $([math]::Round($daysSinceLastModification.TotalDays, 2)) days"

if ($cacheSizeMB -lt 10 -and $daysSinceLastModification.TotalDays -lt 1) {
    Write-Output "Cache seems to be cleared frequently."
} else {
    Write-Output "Cache does not appear to be cleared frequently."
}
