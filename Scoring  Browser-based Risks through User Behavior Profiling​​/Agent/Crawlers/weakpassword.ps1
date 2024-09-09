# Path to Chrome's Login Data SQLite database
$chromeLoginDataPath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Login Data"

# Check if the Login Data file exists
if (-Not (Test-Path $chromeLoginDataPath)) {
    Write-Output "Chrome Login Data file not found."
    exit
}

# Create a temporary copy of the database to avoid locking issues
$tempDbPath = [System.IO.Path]::GetTempFileName()
Copy-Item -Path $chromeLoginDataPath -Destination $tempDbPath -Force

# Query to count the number of insecure credentials
$query = "SELECT COUNT(*) FROM insecure_credentials;"
$result = Invoke-SqliteQuery -DataSource $tempDbPath -Query $query

# Output the result
Write-Output "Number of insecure credentials: $($result[0].'COUNT(*)')"

# Cleanup
Remove-Item -Path $tempDbPath -Force
