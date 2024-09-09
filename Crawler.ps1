# Complete Browser Analysis PowerShell Script with Protocol Scanning

# Function to check if a program is installed
function Is-Installed($program) {
    $installed = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | 
        Where-Object { $_.DisplayName -like "$program" }
    if ($installed) { return $true }
    $installed = Get-ItemProperty HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | 
        Where-Object { $_.DisplayName -like "$program" }
    if ($installed) { return $true }
    return $false
}

# Function to get Chrome version
function Get-ChromeVersion {
    $chromePath = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
    if (-not (Test-Path $chromePath)) {
        $chromePath = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    }
    if (Test-Path $chromePath) {
        $versionInfo = (Get-Item $chromePath).VersionInfo
        return $versionInfo.ProductVersion
    }
    return "Not Found"
}

# Function to get Edge version
function Get-EdgeVersion {
    $edgePath = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe" -ErrorAction SilentlyContinue).'(Default)'
    if ($edgePath -and (Test-Path $edgePath)) {
        $versionInfo = (Get-Item $edgePath).VersionInfo
        return $versionInfo.ProductVersion
    }
    $possiblePaths = @(
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe"
    )
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            $versionInfo = (Get-Item $path).VersionInfo
            return $versionInfo.ProductVersion
        }
    }
    return "Not Found"
}

# Function to get Firefox version
function Get-FirefoxVersion {
    $firefoxPath = "${env:ProgramFiles}\Mozilla Firefox\firefox.exe"
    if (-not (Test-Path $firefoxPath)) {
        $firefoxPath = "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
    }
    if (Test-Path $firefoxPath) {
        $versionInfo = (Get-Item $firefoxPath).VersionInfo
        return $versionInfo.ProductVersion
    }
    return "Not Found"
}

# Function to get Brave version
function Get-BraveVersion {
    $bravePath = "${env:ProgramFiles}\BraveSoftware\Brave-Browser\Application\brave.exe"
    if (-not (Test-Path $bravePath)) {
        $bravePath = "${env:ProgramFiles(x86)}\BraveSoftware\Brave-Browser\Application\brave.exe"
    }
    if (Test-Path $bravePath) {
        $versionInfo = (Get-Item $bravePath).VersionInfo
        return $versionInfo.ProductVersion
    }
    return "Not Found"
}

# Function to get Opera version
function Get-OperaVersion {
    $operaPath = "${env:ProgramFiles}\Opera\launcher.exe"
    if (-not (Test-Path $operaPath)) {
        $operaPath = "${env:ProgramFiles(x86)}\Opera\launcher.exe"
    }
    if (Test-Path $operaPath) {
        $versionInfo = (Get-Item $operaPath).VersionInfo
        return $versionInfo.ProductVersion
    }
    return "Not Found"
}

# Function to check cache clearing frequency
function Get-CacheClearanceFrequency {
    $cachePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"
    if (-Not (Test-Path $cachePath)) {
        return 0
    }
    $lastModified = Get-ChildItem -Recurse -Force -Path $cachePath | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 1 | 
                    Select-Object -ExpandProperty LastWriteTime
    $daysSinceLastModification = (Get-Date) - $lastModified
    if ($daysSinceLastModification.TotalDays -lt 1) {
        return 3  # Cleared frequently
    } elseif ($daysSinceLastModification.TotalDays -lt 7) {
        return 2  # Cleared occasionally
    } else {
        return 1  # Rarely cleared
    }
}

# Function to check hardware access
function Get-HardwareAccess {
    $preferencesPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Preferences"
    if (-Not (Test-Path $preferencesPath)) {
        return 0
    }
    $preferencesJson = Get-Content -Path $preferencesPath | ConvertFrom-Json
    $locationSetting = $preferencesJson.profile.content_settings.exceptions.geolocation
    $cameraSetting = $preferencesJson.profile.content_settings.exceptions.media_stream_camera
    $microphoneSetting = $preferencesJson.profile.content_settings.exceptions.media_stream_mic
    $accessValue = 0
    if ($cameraSetting -and $cameraSetting.PSObject.Properties.Count -gt 0) { $accessValue += 1 }
    if ($microphoneSetting -and $microphoneSetting.PSObject.Properties.Count -gt 0) { $accessValue += 2 }
    if ($locationSetting -and $locationSetting.PSObject.Properties.Count -gt 0) { $accessValue += 4 }
    return $accessValue
}

# Function to get browser extensions
function Get-BrowserExtensions {
    $chromeExtensionsPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Extensions"
    $edgeExtensionsPath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Extensions"
    $extensions = @()
    if (Test-Path $chromeExtensionsPath) {
        $extensions += Get-ChildItem -Path $chromeExtensionsPath | 
                       Where-Object { $_.PSIsContainer } | 
                       Select-Object -ExpandProperty Name
    }
    if (Test-Path $edgeExtensionsPath) {
        $extensions += Get-ChildItem -Path $edgeExtensionsPath | 
                       Where-Object { $_.PSIsContainer } | 
                       Select-Object -ExpandProperty Name
    }
    return $extensions
}

# Function to check for malicious files
function Get-MaliciousFiles {
    $virusTotalApiKey = "4acef1aa248a0ee5eac667c1e8cef287f4d9034f49bbd0da33fb2ffa2447376f"
    $downloadPath = "$env:USERPROFILE\Downloads\test"
    function Get-FileHashValue {
        param ([string]$filePath)
        if (Test-Path $filePath) {
            $hash = Get-FileHash -Path $filePath -Algorithm SHA256
            return $hash.Hash
        }
        return $null
    }
    function Check-FileOnVirusTotal {
        param ([string]$fileHash)
        $uri = "https://www.virustotal.com/api/v3/files/$fileHash"
        $headers = @{ "x-apikey" = $virusTotalApiKey }
        try {
            $response = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
            return ($response.data.attributes.last_analysis_stats.malicious -gt 0)
        } catch {
            Write-Host "Failed to check file on VirusTotal: $($_.Exception.Message)" -ForegroundColor Yellow
            return $false
        }
    }
    $maliciousCount = 0
    if (Test-Path $downloadPath) {
        $files = Get-ChildItem -Path $downloadPath -Recurse -File
        $totalFiles = $files.Count
        $processedFiles = 0
        foreach ($file in $files) {
            $processedFiles++
            Write-Progress -Activity "Scanning files" -Status "Processed $processedFiles of $totalFiles" -PercentComplete (($processedFiles / $totalFiles) * 100)
            $fileHash = Get-FileHashValue -filePath $file.FullName
            if ($fileHash -and (Check-FileOnVirusTotal -fileHash $fileHash)) {
                $maliciousCount++
                Write-Host "Potentially malicious file detected: $($file.Name)" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Download directory not found: $downloadPath" -ForegroundColor Yellow
    }
    Write-Host "Total potentially malicious files detected: $maliciousCount" -ForegroundColor Cyan
    return $maliciousCount
}

# Function to analyze Chrome cookies
function Get-ChromeCookies {
    $cookiesDbPath = "C:\Project\Cookies"
    if (-not (Test-Path $cookiesDbPath)) {
        Write-Host "Error: Cookies file not found at $cookiesDbPath" -ForegroundColor Red
        return $null
    }
    $dllPath = Join-Path $PSScriptRoot "System.Data.SQLite.dll"
    if (-not (Test-Path $dllPath)) {
        Write-Host "Error: System.Data.SQLite.dll not found in the script directory." -ForegroundColor Red
        return $null
    }
    Add-Type -Path $dllPath
    $connectionString = "Data Source=$cookiesDbPath;Version=3;Read Only=True;"
    try {
        $connection = New-Object System.Data.SQLite.SQLiteConnection($connectionString)
        $connection.Open()
        $query = @"
        SELECT host_key, name, CASE WHEN is_secure = 1 THEN 'Yes' ELSE 'No' END as secure,
        CASE WHEN is_httponly = 1 THEN 'Yes' ELSE 'No' END as httponly,
        CASE WHEN samesite = 0 THEN 'None' WHEN samesite = 1 THEN 'Lax' WHEN samesite = 2 THEN 'Strict' ELSE 'Unknown' END as samesite
        FROM cookies
"@
        $command = $connection.CreateCommand()
        $command.CommandText = $query
        $adapter = New-Object System.Data.SQLite.SQLiteDataAdapter($command)
        $dataset = New-Object System.Data.DataSet
        $adapter.Fill($dataset)
        return $dataset.Tables[0]
    }
    catch {
        Write-Host "Error accessing the Cookies database: $_" -ForegroundColor Red
        return $null
    }
    finally {
        if ($connection -and $connection.State -eq 'Open') {
            $connection.Close()
        }
    }
}

function Get-UnsecureCookieCount {
    $cookies = Get-ChromeCookies
    if ($null -eq $cookies -or $cookies.Rows.Count -eq 0) {
        Write-Host "No cookies found or unable to access cookie data." -ForegroundColor Yellow
        return 0
    }
    $unsecureCookies = $cookies | Where-Object { $_.secure -eq 'No' }
    return $unsecureCookies.Count
}

# Function to check if Safe Browsing is enabled in Chrome
function Get-ChromeSafeBrowsingStatus {
    $prefPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Preferences"
    if (Test-Path $prefPath) {
        try {
            $prefContent = Get-Content $prefPath -Raw | ConvertFrom-Json
            if ($null -ne $prefContent.safebrowsing) {
                $safeBrowsingEnabled = $prefContent.safebrowsing.enabled
                if ($safeBrowsingEnabled -eq $true) {
                    return $false  # Safe Browsing is enabled, so DisabledSafeBrowsing should be false
                } elseif ($safeBrowsingEnabled -eq $false) {
                    return $true   # Safe Browsing is disabled, so DisabledSafeBrowsing should be true
                } else {
                    return $false  # Unable to determine, assume it's enabled (DisabledSafeBrowsing should be false)
                }
            } else {
                return $false  # Safe Browsing section not found, assume it's enabled (DisabledSafeBrowsing should be false)
            }
        } catch {
            Write-Host "An error occurred while reading Chrome preferences: $_" -ForegroundColor Yellow
            return $false  # Assume it's enabled in case of error (DisabledSafeBrowsing should be false)
        }
    } else {
        Write-Host "Chrome Preferences file not found. Make sure Chrome is installed and has been run at least once." -ForegroundColor Yellow
        return $false  # Assume it's enabled if we can't find the file (DisabledSafeBrowsing should be false)
    }
}

# Function to check for insecure credentials in Chrome
function Get-ChromeInsecureCredentials {
    $loginDataPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Login Data"
    if (-not (Test-Path $loginDataPath)) {
        Write-Host "Chrome Login Data file not found." -ForegroundColor Yellow
        return 0
    }

    $tempFile = [System.IO.Path]::GetTempFileName()
    $connection = $null
    try {
        Copy-Item -Path $loginDataPath -Destination $tempFile -Force

        $connectionString = "Data Source=$tempFile;Version=3;New=True;Compress=True;"
        $connection = New-Object System.Data.SQLite.SQLiteConnection($connectionString)
        $connection.Open()

        $query = "SELECT COUNT(*) FROM logins WHERE origin_url LIKE 'http://%'"
        $command = $connection.CreateCommand()
        $command.CommandText = $query

        $count = $command.ExecuteScalar()
        return $count
    }
    catch {
        Write-Host "Error accessing Chrome Login Data: $_" -ForegroundColor Red
        return 0
    }
    finally {
        if ($connection -and $connection.State -eq 'Open') {
            $connection.Close()
        }
        $connection.Dispose()
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
        
        # Try to remove the file, but don't throw an error if it fails
        try {
            Remove-Item -Path $tempFile -Force -ErrorAction Stop
        }
        catch {
            Write-Host "Warning: Could not remove temporary file $tempFile. You may want to delete it manually." -ForegroundColor Yellow
        }
    }
}

# Function to check registry for protocol
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



# Function to count protocol instances
function Count-ProtocolInstances {
    param (
        [string]$Protocol,
        [string]$Path,
        [string[]]$ExcludeDirs
    )
    $count = 0
    $files = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
             Where-Object { 
                 $_.Extension -in @(".htm", ".html", ".txt", ".log", ".js", ".css") -and
                 ($ExcludeDirs.Count -eq 0 -or ($ExcludeDirs | Where-Object { $_.FullName -notlike "*$_*" }))
             }
    
    foreach ($file in $files) {
        try {
            $content = Get-Content -Path $file.FullName -Raw -ErrorAction Stop
            if ($null -ne $content) {
                $matches = ([regex]::Matches($content, [regex]::Escape($Protocol))).Count
                $count += $matches
                if ($matches -gt 0) {
                    Write-Host "Found $matches instance(s) of $Protocol in file: $($file.FullName)"
                }
            }
        }
        catch {
            Write-Host "Unable to read file: $($file.FullName) - $($_.Exception.Message)"
        }
    }
    return $count
}

# Main script execution
function Main {
    Write-Host "Starting browser analysis..." -ForegroundColor Cyan

    $browsers = @(
        "Google Chrome",
        "Mozilla Firefox",
        "Microsoft Edge",
        "Opera",
        "Safari",
        "Brave",
        "Vivaldi",
        "Internet Explorer"
    )

    $installedBrowsers = @()
    $browserVersions = @{}

    Write-Host "Detecting installed browsers..." -ForegroundColor Yellow
    foreach ($browser in $browsers) {
        if (Is-Installed $browser) {
            $installedBrowsers += $browser
            Write-Host "- $browser detected" -ForegroundColor Green
        }
    }

    foreach ($browser in $installedBrowsers) {
        Write-Host "Checking $browser version..." -ForegroundColor Yellow
        switch -Wildcard ($browser) {
            "*Chrome*" { $browserVersions[$browser] = Get-ChromeVersion }
            "*Edge*" { $browserVersions[$browser] = Get-EdgeVersion }
            "*Firefox*" { $browserVersions[$browser] = Get-FirefoxVersion }
            "*Brave*" { $browserVersions[$browser] = Get-BraveVersion }
            "*Opera*" { $browserVersions[$browser] = Get-OperaVersion }
            default { $browserVersions[$browser] = "Version check not implemented" }
        }
    }

    Write-Host "Checking default browser..." -ForegroundColor Yellow
    $defaultBrowser = (Get-ItemProperty HKCU:\Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice -ErrorAction SilentlyContinue).ProgId
    $defaultBrowser = if ($defaultBrowser) { $defaultBrowser } else { "Unknown" }
    Write-Host "Default browser: $defaultBrowser" -ForegroundColor Green
    
    Write-Host "Analyzing cache clearance frequency..." -ForegroundColor Yellow
    $cacheFrequency = Get-CacheClearanceFrequency
    
    Write-Host "Checking hardware access permissions..." -ForegroundColor Yellow
    $hardwareAccess = Get-HardwareAccess
    $hardwareAccessMessage = switch ($hardwareAccess) {
        0 { "No permissions allowed" }
        1 { "Only camera allowed" }
        2 { "Only microphone allowed" }
        3 { "Camera and microphone allowed" }
        4 { "Only location allowed" }
        5 { "Location and camera allowed" }
        6 { "Location and microphone allowed" }
        7 { "All permissions allowed (camera, microphone, and location)" }
        default { "Unknown permission combination" }
    }
    Write-Host "Hardware Access: $hardwareAccessMessage" -ForegroundColor Green
    
    Write-Host "Gathering browser extensions..." -ForegroundColor Yellow
    $extensions = Get-BrowserExtensions
    
    Write-Host "Scanning for potentially malicious files (this may take a while)..." -ForegroundColor Yellow
    $maliciousFileCount = Get-MaliciousFiles

    Write-Host "Analyzing Chrome cookies..." -ForegroundColor Yellow
    $unsecureCookieCount = Get-UnsecureCookieCount

    Write-Host "Checking Chrome Safe Browsing status..." -ForegroundColor Yellow
    $disabledSafeBrowsing = Get-ChromeSafeBrowsingStatus
    if ($disabledSafeBrowsing) {
        Write-Host "Safe Browsing is disabled in Chrome." -ForegroundColor Red
    } else {
        Write-Host "Safe Browsing is enabled in Chrome." -ForegroundColor Green
    }

    Write-Host "Checking for insecure credentials in Chrome..." -ForegroundColor Yellow
    $insecureCredentialsCount = Get-ChromeInsecureCredentials
    Write-Host "Number of insecure credentials: $insecureCredentialsCount" -ForegroundColor Green

    # List of potentially unsecure protocols
    $unsecureProtocols = @("http:", "ftp:", "telnet:", "gopher:")
    
    # Initialize result hashtable for protocols
    $protocolResults = @{}
    foreach ($protocol in $unsecureProtocols) {
        $protocolResults[$protocol] = 0
    }

    # Check Windows Registry for protocol associations
    Write-Host "Checking Windows Registry for protocol associations..." -ForegroundColor Yellow
    foreach ($protocol in $unsecureProtocols) {
        $protocolResults[$protocol] += Check-RegistryForProtocol -Protocol $protocol
    }

    # Check common browser bookmark and history locations
    $browserPaths = @(
        "$env:LOCALAPPDATA\Google\Chrome\User Data\Default",
        "$env:APPDATA\Mozilla\Firefox\Profiles",
        "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default"
    )

    # Directories to exclude
    $excludeDirs = @("Extensions", "Cache")

    Write-Host "Searching for unsecure protocols in browser data..." -ForegroundColor Yellow
    foreach ($path in $browserPaths) {
        if (Test-Path $path) {
            Write-Host "Checking in $path" -ForegroundColor Cyan
            foreach ($protocol in $unsecureProtocols) {
                $count = Count-ProtocolInstances -Protocol $protocol -Path $path -ExcludeDirs $excludeDirs
                $protocolResults[$protocol] += $count
                if ($count -eq 0) {
                    Write-Host "No instances of $protocol found in $path" -ForegroundColor Green
                }
            }
        }
    }

    # Prepare the log entry (flattened structure)
    $logEntry = [ordered]@{
        "@timestamp" = (Get-Date).ToString("o")  # ISO 8601 format
        host = @{
            name = $env:COMPUTERNAME
        }
        user = @{
            name = $env:USERNAME
        }
        browser = @{
            installed = $installedBrowsers
            chrome = @{
                version = if ($browserVersions.ContainsKey("Google Chrome")) { $browserVersions["Google Chrome"] } else { "Not installed" }
            }
            edge = @{
                version = if ($browserVersions.ContainsKey("Microsoft Edge")) { $browserVersions["Microsoft Edge"] } else { "Not installed" }
            }
            brave = @{
                version = if ($browserVersions.ContainsKey("Brave")) { $browserVersions["Brave"] } else { "Not installed" }
            }
            default = $defaultBrowser
        }
        UnsecureProtocol = [int]($protocolResults.Values | Measure-Object -Sum).Sum
        HttpConnections = [int]($protocolResults["http:"])
        FtpConnections = [int]($protocolResults["ftp:"])
        TelnetConnections = [int]($protocolResults["telnet:"])
        GopherConnections = [int]($protocolResults["gopher:"])
        WeakPassMgmt = [int]$insecureCredentialsCount
        DisabledSafeBrowsing = $disabledSafeBrowsing -eq $true  # Ensure it's a boolean
        BlockedPopUps = $true  # Placeholder
        ThrirdPartyCookies = if ($null -eq $unsecureCookieCount) { 0 } else { [int]$unsecureCookieCount }
        MalDownload = if ($null -eq $maliciousFileCount) { 0 } else { [int]$maliciousFileCount }
        Cache = if ($null -eq $cacheFrequency) { 0 } else { [int]$cacheFrequency }
        HardwareAccess = if ($null -eq $hardwareAccess) { 0 } else { [int]$hardwareAccess }
        MalExt = if ($extensions.Count -gt 0) { $extensions } else { @() }
    }

    # Convert to JSON and output to file
    $jsonOutput = $logEntry | ConvertTo-Json -Depth 10 -Compress
    $outputPath = "C:\Project\test.log"
    
    Write-Host "Writing results to $outputPath..." -ForegroundColor Yellow
    
    # Use UTF8Encoding without BOM
    $utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::AppendAllText($outputPath, $jsonOutput + "`n`n")  # Add two newline characters
    
    Write-Host "Analysis complete. Results have been appended to $outputPath" -ForegroundColor Green

    # Display summary of results
    Write-Host "`nSummary of potentially unsecure protocol usage:" -ForegroundColor Cyan
    foreach ($protocol in $unsecureProtocols) {
        Write-Host "$protocol : $($protocolResults[$protocol]) instance(s) found" -ForegroundColor Yellow
    }
    Write-Host "Total unsecure connections: $(($protocolResults.Values | Measure-Object -Sum).Sum)" -ForegroundColor Red
}

# Run the main function
Main