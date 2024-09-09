# Function to locate the Chrome Preferences file
function Find-ChromePreferences {
    $localAppDataPath = $env:LOCALAPPDATA
    $chromeDefaultProfilePath = "$localAppDataPath\Google\Chrome\User Data\Default\Preferences"
    $chromeUserProfilesPath = "$localAppDataPath\Google\Chrome\User Data\"

    if (Test-Path $chromeDefaultProfilePath) {
        return $chromeDefaultProfilePath
    }

    $profileFolders = Get-ChildItem -Path $chromeUserProfilesPath -Directory | Where-Object { $_.Name -match '^Profile \d+$' }
    
    foreach ($profile in $profileFolders) {
        $preferencesFilePath = "$($profile.FullName)\Preferences"
        if (Test-Path $preferencesFilePath) {
            return $preferencesFilePath
        }
    }
    return $null
}

# Get the path to the Preferences file
$preferencesPath = Find-ChromePreferences

if (-Not $preferencesPath) {
    Write-Output "No valid Chrome Preferences file found."
    exit
} else {
    Write-Output "Chrome Preferences file found at: $preferencesPath"
}

$preferencesJson = Get-Content -Path $preferencesPath | Out-String | ConvertFrom-Json

# Extract settings related to location, camera, and microphone
$locationSetting = $preferencesJson.profile.content_settings.exceptions.geolocation
$cameraSetting = $preferencesJson.profile.content_settings.exceptions.media_stream_camera
$microphoneSetting = $preferencesJson.profile.content_settings.exceptions.media_stream_mic

# Function to check access settings and handle missing data
function Check-Access {
    param (
        $setting,
        $name
    )

    if ($setting -ne $null -and $setting.PSObject.Properties.Count -gt 0) {
        foreach ($site in $setting.PSObject.Properties.Name) {
            $accessLevel = $setting.$site.setting
            $accessStatus = switch ($accessLevel) {
                1 { "Allowed" }
                2 { "Blocked" }
                default { "Unknown" }
            }
            Write-Output "$name access for ${site}: $accessStatus"
        }
    } else {
        Write-Output "$name access: Not Found"
    }
}

# Check location, camera, and microphone access
Check-Access -setting $locationSetting -name "Location"
Check-Access -setting $cameraSetting -name "Camera"
Check-Access -setting $microphoneSetting -name "Microphone"

# Ensure that all three settings (Location, Camera, Microphone) are accounted for
if (-not $locationSetting) {
    Write-Output "Location access: Not Found"
}
if (-not $cameraSetting) {
    Write-Output "Camera access: Not Found"
}
if (-not $microphoneSetting) {
    Write-Output "Microphone access: Not Found"
}
