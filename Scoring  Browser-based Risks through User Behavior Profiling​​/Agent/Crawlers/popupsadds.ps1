# Function to locate the Chrome Preferences file
function Find-ChromePreferences {
    $localAppDataPath = $env:LOCALAPPDATA
    $chromeDefaultProfilePath = "$localAppDataPath\Google\Chrome\User Data\Default\Preferences"

    if (Test-Path $chromeDefaultProfilePath) {
        return $chromeDefaultProfilePath
    } else {
        Write-Output "Chrome Preferences file not found."
        exit
    }
}

# Function to check content settings and count allowed instances
function Check-ContentSettings {
    param (
        $setting
    )

    # Initialize counter for allowed settings
    $allowedCount = 0

    if ($setting -ne $null) {
        foreach ($site in $setting.PSObject.Properties.Name) {
            $accessLevel = $setting.$site.setting
            if ($accessLevel -eq 1) {
                $allowedCount++
            }
        }
    }

    # Return the total number of allowed settings
    return $allowedCount
}

# Find Chrome Preferences file
$preferencesPath = Find-ChromePreferences

# Read the Preferences file content
$preferencesJson = Get-Content -Path $preferencesPath -Raw | ConvertFrom-Json

# Extract the settings related to Pop-ups and Ads
$popupsSetting = $preferencesJson.profile.content_settings.exceptions.popups
$adsSetting = $preferencesJson.profile.content_settings.exceptions.ads

# Check Pop-ups and Ads settings and count allowed instances
$allowedPopups = Check-ContentSettings -setting $popupsSetting
$allowedAds = Check-ContentSettings -setting $adsSetting

# Calculate the total of allowed pop-ups and ads
$totalAllowed = $allowedPopups + $allowedAds

# Output the total counts of allowed pop-ups, ads, and combined total
Write-Output "$totalAllowed"
