# PowerShell script to count instances of potentially unsecure protocols in browsers

function Check-RegistryForProtocol {
    param (
        [string]$Protocol
    )
    $registryPath = "HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\$Protocol\UserChoice"
    if (Test-Path $registryPath) {
        $handler = (Get-ItemProperty -Path $registryPath -Name ProgId).ProgId
        Write-Host "Protocol $Protocol is associated with: $handler"
        return 1
    }
    return 0
}

function Count-ProtocolInstances {
    param (
        [string]$Protocol,
        [string]$Path
    )
    $count = 0
    $files = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
             Where-Object { $_.Extension -in @(".htm", ".html", ".txt", ".log") }
    
    foreach ($file in $files) {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue
        $matches = ([regex]::Matches($content, [regex]::Escape($Protocol))).Count
        $count += $matches
        if ($matches -gt 0) {
            Write-Host "Found $matches instance(s) of $Protocol in file: $($file.FullName)"
        }
    }
    return $count
}

# List of potentially unsecure protocols
$unsecureProtocols = @("http:", "ftp:", "telnet:", "gopher:")

# Initialize result hashtable
$results = @{}
foreach ($protocol in $unsecureProtocols) {
    $results[$protocol] = 0
}

# Check Windows Registry for protocol associations
Write-Host "Checking Windows Registry for protocol associations..."
foreach ($protocol in $unsecureProtocols) {
    $results[$protocol] += Check-RegistryForProtocol -Protocol $protocol
}

# Check common browser bookmark and history locations
$browserPaths = @(
    "$env:LOCALAPPDATA\Google\Chrome\User Data\Default",
    "$env:APPDATA\Mozilla\Firefox\Profiles",
    "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default"
)

Write-Host "`nSearching for unsecure protocols in browser data..."
foreach ($path in $browserPaths) {
    if (Test-Path $path) {
        Write-Host "Checking in $path"
        foreach ($protocol in $unsecureProtocols) {
            $count = Count-ProtocolInstances -Protocol $protocol -Path $path
            $results[$protocol] += $count
            if ($count -eq 0) {
                Write-Host "No instances of $protocol found in $path"
            }
        }
    }
}

# Display summary of results
Write-Host "`nSummary of potentially unsecure protocol usage:"
foreach ($protocol in $unsecureProtocols) {
    Write-Host "$protocol : $($results[$protocol]) instance(s) found"
}

Write-Host "`nSearch complete. Please review the results above."
Write-Host "Note: This script provides a general indication and may not catch all instances of unsecure protocol usage."
Write-Host "For a more comprehensive analysis, consider using specialized security auditing tools."