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

        # Handle the BrowsingDataLifetime policy (dictionary format with specific structure)
        # Apply the BrowsingDataLifetime policy as a REG_SZ JSON string under the correct subkey with numeric value names
        if ($policyName -eq 'BrowsingDataLifetime') {
            try {
                if ($policyValue -is [array]) {
                    # Ensure the 'BrowsingDataLifetime' registry path exists
                    $browsingDataLifetimePath = "$registryPath\BrowsingDataLifetime"
                    if (-not (Test-Path "Registry::$browsingDataLifetimePath")) {
                        New-Item -Path "Registry::$browsingDataLifetimePath" -Force | Out-Null
                        Write-Host "$($browserName): Created registry path at $browsingDataLifetimePath"
                    }

                    # Apply each entry with a numbered key
                    for ($i = 0; $i -lt $policyValue.Count; $i++) {
                        $entry = $policyValue[$i]
                        if (-not $entry.data_types -or -not $entry.time_to_live_in_hours) {
                            Write-Error "$($browserName): BrowsingDataLifetime entry is missing necessary fields."
                            continue
                        }

                        # Convert the entry to a JSON string
                        $jsonString = $entry | ConvertTo-Json -Compress

                        # Assign a numeric key starting from 1
                        $keyName = ($i + 1).ToString()

                        # Apply the policy as a REG_SZ string with the numeric key
                        Set-ItemProperty -Path "Registry::$browsingDataLifetimePath" -Name $keyName -Value $jsonString -Type String -Force
                        Write-Host "$($browserName): BrowsingDataLifetime set for $($entry.data_types) under key $keyName"
                    }
                } else {
                    Write-Error "$($browserName): BrowsingDataLifetime format is invalid."
                }
            } catch {
                Write-Error "$($browserName): Failed to apply BrowsingDataLifetime policy. Error: $_"
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
            # Handle policies expecting DWORD (integer) values
            try {
                if ($policyValue -is [array]) {
                    Write-Error "$($browserName): $($policyName) has an invalid format and cannot be applied as a UInt32."
                    continue
                }

                $intValue = [int]$policyValue
                Set-ItemProperty -Path "Registry::$registryPath" -Name $policyName -Value $intValue -Type DWord -Force
                Write-Host "$($browserName): $($policyName) set to $intValue"
            } catch {
                Write-Error "$($browserName): Failed to apply $($policyName) to $registryPath due to type conversion error."
            }
        }
    }
}

Write-Host "All policies have been applied successfully."
