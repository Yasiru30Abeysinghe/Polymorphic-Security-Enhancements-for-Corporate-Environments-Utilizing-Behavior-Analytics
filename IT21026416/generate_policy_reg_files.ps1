param (
    [string]$jsonFilePath
)

# Check if jsonFilePath is provided
if (-not $jsonFilePath) {
    Write-Error "jsonFilePath is not specified."
    exit 1
}

# Load the policies from the JSON file
if (-not (Test-Path $jsonFilePath)) {
    Write-Error "Policies file $jsonFilePath not found."
    exit 1
}

# Read the JSON file and convert to PowerShell object
$policies = Get-Content -Path $jsonFilePath | ConvertFrom-Json

# Apply policies directly to the registry for each browser
foreach ($browser in $policies.PSObject.Properties) {
    $browserName = $browser.Name
    $registryPath = $browser.Value.registry_path
    $policySettings = $browser.Value.policies

    # Ensure the general registry path exists, create it if it doesn't
    if (-not (Test-Path "Registry::$registryPath")) {
        New-Item -Path "Registry::$registryPath" -Force | Out-Null
        Write-Host "$($browserName): Registry path created at $registryPath"
    }

    # Apply each policy in the JSON file
    foreach ($policy in $policySettings.PSObject.Properties) {
        $policyName = $policy.Name
        $policyValue = $policy.Value

        # Handle policies expecting DWORD (integer) values
        if ($policyName -in @('DefaultGeolocationSetting', 'VideoCaptureAllowed', 'DefaultSensorsSetting', 'DefaultNotificationsSetting', 'DefaultJavaScriptSetting', 'DefaultImagesSetting', 'DefaultPopupsSetting', 'DefaultWebUsbGuardSetting')) {
            try {
                # Convert the value to an integer if it's not already a number
                if ($policyValue -is [array]) {
                    $intValue = [int]$policyValue[0]
                } else {
                    $intValue = [int]$policyValue
                }
                Set-ItemProperty -Path "Registry::$registryPath" -Name $policyName -Value $intValue -Type DWord -Force
                Write-Host "$($browserName): $($policyName) set to $intValue"
            } catch {
                Write-Error "$($browserName): Failed to apply $($policyName) to $registryPath due to type conversion error."
            }
        }
        # Handle ExtensionInstallAllowlist and ExtensionInstallBlocklist (arrays)
        elseif ($policyName -in @('ExtensionInstallAllowlist', 'ExtensionInstallBlocklist')) {
            try {
                if ($policyValue -is [array]) {
                    # Remove existing numbered keys (if necessary)
                    Remove-ItemProperty -Path "Registry::$registryPath\$policyName" -Name * -ErrorAction SilentlyContinue

                    # Add each extension ID under numbered subkeys
                    for ($i = 0; $i -lt $policyValue.Count; $i++) {
                        $extensionId = $policyValue[$i]
                        $subKey = $i + 1  # Registry keys are numbered starting from 1
                        New-ItemProperty -Path "Registry::$registryPath\$policyName" -Name $subKey -Value $extensionId -Force
                        Write-Host "$($browserName): Added $($extensionId) to $($policyName) as entry $subKey"
                    }
                } else {
                    Write-Error "$($browserName): $($policyName) is not a valid array of extension IDs."
                }
            } catch {
                Write-Error "$($browserName): Failed to apply $($policyName) to $registryPath"
            }
        }
        # Handle URLBlocklist and URLAllowlist (arrays of URLs)
        elseif ($policyName -in @('URLBlocklist', 'URLAllowlist')) {
            try {
                if ($policyValue -is [array]) {
                    # Ensure the registry path for URLBlocklist or URLAllowlist exists
                    if (-not (Test-Path "Registry::$registryPath\$policyName")) {
                        New-Item -Path "Registry::$registryPath\$policyName" -Force | Out-Null
                        Write-Host "$($browserName): Created registry path for $($policyName)"
                    }

                    # Remove existing numbered keys (if necessary)
                    Remove-ItemProperty -Path "Registry::$registryPath\$policyName" -Name * -ErrorAction SilentlyContinue

                    # Add each URL under numbered subkeys
                    for ($i = 0; $i -lt $policyValue.Count; $i++) {
                        $url = $policyValue[$i]
                        $subKey = $i + 1  # Registry keys are numbered starting from 1
                        New-ItemProperty -Path "Registry::$registryPath\$policyName" -Name $subKey -Value $url -Force
                        Write-Host "$($browserName): Added $($url) to $($policyName) as entry $subKey"
                    }
                } else {
                    Write-Error "$($browserName): $($policyName) is not a valid array of URLs."
                }
            } catch {
                Write-Error "$($browserName): Failed to apply $($policyName) to $registryPath"
            }
        }
        else {
            # Apply other policies at the general registry path
            try {
                # Skip policies with array values that shouldn't be converted to UInt32
                if ($policyValue -is [array]) {
                    Write-Error "$($browserName): $($policyName) has an invalid format and cannot be applied as a UInt32."
                    continue
                }

                # Convert to UInt32 only if the value isn't an array
                [UInt32]$policyValue = [UInt32]$policyValue

                Set-ItemProperty -Path "Registry::$registryPath" -Name $policyName -Value $policyValue -Type DWord -Force
                Write-Host "$($browserName): $($policyName) applied to $registryPath"
            }
            catch {
                Write-Error "$($browserName): Failed to apply $($policyName) to $registryPath"
            }
        }
    }
}

Write-Host "All policies have been applied successfully."
