# VirusTotal API key (replace with your actual API key)
$virusTotalApiKey = "4acef1aa248a0ee5eac667c1e8cef287f4d9034f49bbd0da33fb2ffa2447376f"

# Function to get file hash
function Get-FileHashValue {
    param (
        [string]$filePath
    )

    if (Test-Path $filePath) {
        $hash = Get-FileHash -Path $filePath -Algorithm SHA256
        return $hash.Hash
    } else {
        return $null
    }
}

# Function to check file hash on VirusTotal
function Check-FileOnVirusTotal {
    param (
        [string]$fileHash
    )

    $uri = "https://www.virustotal.com/api/v3/files/$fileHash"
    $headers = @{ "x-apikey" = $virusTotalApiKey }
    
    try {
        $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
        
        # Check if the file is flagged as malicious
        if ($response.data.attributes.last_analysis_stats.malicious -gt 0) {
            return $true
        } else {
            return $false
        }
    } catch {
        Write-Output "Failed to check file on VirusTotal: $($_.Exception.Message)"
        return $false
    }
}

# Function to scan a directory for files and count malicious ones
function Scan-DirectoryForMalware {
    param (
        [string]$directoryPath
    )

    $maliciousCount = 0

    if (Test-Path $directoryPath) {
        $files = Get-ChildItem -Path $directoryPath -Recurse -File
        foreach ($file in $files) {
            $fileHash = Get-FileHashValue -filePath $file.FullName
            if ($fileHash -ne $null) {
                if (Check-FileOnVirusTotal -fileHash $fileHash) {
                    $maliciousCount++
                }
            }
        }
    } else {
        Write-Output "Directory not found: $directoryPath"
    }

    return $maliciousCount
}

# Define the download directory path (same for Chrome and Edge)
$downloadPath = "C:\Users\yasir\Downloads\test"

Write-Output "Scanning for potentially malicious files..."

# Scan downloads
$maliciousCount = Scan-DirectoryForMalware -directoryPath $downloadPath

# Output the total count of malicious files
Write-Output "`nTotal malicious files detected: $maliciousCount"
