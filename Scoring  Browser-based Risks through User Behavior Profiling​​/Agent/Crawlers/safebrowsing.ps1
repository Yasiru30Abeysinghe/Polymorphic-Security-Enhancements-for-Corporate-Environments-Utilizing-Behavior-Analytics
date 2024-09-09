# PowerShell script to check if Safe Browsing is enabled in Chrome

# Define the path to the Chrome Preferences file
$prefPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Preferences"

# Check if the Preferences file exists
if (Test-Path $prefPath) {
    try {
        # Read the contents of the Preferences file
        $prefContent = Get-Content $prefPath -Raw | ConvertFrom-Json

        # Check if the safe_browsing section exists
        if ($prefContent.safebrowsing -ne $null) {
            # Check the status of Safe Browsing
            $safeBrowsingEnabled = $prefContent.safebrowsing.enabled

            if ($safeBrowsingEnabled -eq $true) {
                Write-Host "Safe Browsing is enabled in Chrome."
            } elseif ($safeBrowsingEnabled -eq $false) {
                Write-Host "Safe Browsing is disabled in Chrome."
            } else {
                Write-Host "Unable to determine Safe Browsing status. It may be set to default (enabled)."
            }
        } else {
            Write-Host "Safe Browsing section not found in Chrome preferences. It may be set to default (enabled)."
        }
    } catch {
        Write-Host "An error occurred while reading Chrome preferences: $_"
    }
} else {
    Write-Host "Chrome Preferences file not found. Make sure Chrome is installed and has been run at least once."
}