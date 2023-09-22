$orgName = "SKY-UK"
$outputFile = "github_dashboard_data.csv"

# Fetch the token from the environment variable
$token = $env:GITHUB_PAT

$headers = @{
    "Accept" = "application/vnd.github.v3+json"
    "Authorization" = "Bearer $token"
}

# Create a new CSV file and write the headers
"Repository,Last Commit Date,Committer,Repo Admin Access,Creation Date,Creator,Is Archived,Repo Size (KB)" | Out-File $outputFile

# Function to handle rate limiting
function HandleRateLimit {
    param (
        [System.Net.HttpWebResponse]$response
    )

    $remaining = $response.Headers["X-RateLimit-Remaining"]
    if ($remaining -eq 0) {
        $resetTime = $response.Headers["X-RateLimit-Reset"]
        $currentTime = [System.DateTimeOffset]::Now.ToUnixTimeSeconds()
        $waitTime = $resetTime - $currentTime + 10  # Adding 10 seconds buffer

        Write-Warning "Rate limit reached. Waiting for $($waitTime) seconds."
        Start-Sleep -Seconds $waitTime
    }
}

# Loop through pages of repositories
$page = 1
do {
    $repos = @()
    try {
        $repos = Invoke-RestMethod -Uri "https://api.github.com/orgs/$orgName/repos?per_page=100&page=$page" -Headers $headers
    } catch {
        HandleRateLimit $_.Exception.Response
        $repos = Invoke-RestMethod -Uri "https://api.github.com/orgs/$orgName/repos?per_page=100&page=$page" -Headers $headers
    }

    foreach ($repo in $repos) {
        # Fetch the last commit for the repository
        try {
            $commitInfo = Invoke-RestMethod -Uri $repo.commits_url.Replace("{/sha}", "?per_page=1") -Headers $headers
            $commitDate = $commitInfo[0].commit.author.date
            $committer = $commitInfo[0].commit.author.name
        } catch {
            if ($_.Exception.Message -like "*no commit found*") {
                $commitDate = "<Never Committed>"
                $committer = "<N/A>"
            } else {
                HandleRateLimit $_.Exception.Response
                continue
            }
        }

        # Fetch the actual user who created the repository
        $creator = "<Unknown>"
        try {
            $events = Invoke-RestMethod -Uri $repo.events_url -Headers $headers
            $creationEvent = $events | Where-Object { $_.type -eq "CreateEvent" } | Select-Object -First 1
            if ($creationEvent) {
                $creator = $creationEvent.actor.login
            }
        } catch {
            HandleRateLimit $_.Exception.Response
        }

        # Extract repository details
        $repoAdminAccess = $repo.permissions.admin
        $creationDate = $repo.created_at
        $isArchived = $repo.archived
        $repoSize = $repo.size

        # Write the details to the CSV file
        "$($repo.name),$commitDate,$committer,$repoAdminAccess,$creationDate,$creator,$isArchived,$repoSize" | Out-File $outputFile -Append
    }

    $page++
} while ($repos.Count -eq 100)

Write-Output "Results saved to $outputFile"
