$orgName = "SKY-UK"  
$outputFile = "detailed_repos_info.csv"

# Fetch the token from the environment variable
$token = $env:GITHUB_PAT

if (-not $token) {
    Write-Error "GITHUB_PAT environment variable not set. Please set it with your GitHub Personal Access Token."
    exit
}

$headers = @{
    "Accept" = "application/vnd.github.v3+json"
    "Authorization" = "token $token"
}

# Create a new CSV file and write the headers
"Repository,Last Commit Date,Committer,Repo Admin Access,Creation Date,Creator,Is Archived,Repo Size (KB),Open Issues,Open PRs,Language,License,Visibility,Stars,Forks,Watches,Alarm" | Out-File $outputFile

# Fetch all repositories for the organization
$repos = $null
$endpoint = "https://api.github.com/orgs/$orgName/repos?per_page=500"
do {
    try {
        $repos = Invoke-RestMethod -Uri $endpoint -Headers $headers
    } catch {
        Write-Warning "Error fetching repositories for organization: $orgName. Error: $($_.Exception.Message)"
        exit
    }

    foreach ($repo in $repos) {
        # Initialize default values for repositories with potential issues
        $commitDate = "<Never Committed>"
        $committer = "<N/A>"

        try {
            # Fetch the last commit for the repository
            $commitInfo = Invoke-RestMethod -Uri $repo.commits_url -replace "{/sha}", "?per_page=1" -Headers $headers
            $commitDate = $commitInfo[0].commit.author.date
            $committer = $commitInfo[0].commit.author.name
        } catch {
            if ($_.Exception.Message -like "*no commit found*") {
                Write-Warning "No commits found for repository: $($repo.name)"
            } elseif ($_.Exception.Message -like "*HTTP 409*") {
                Write-Warning "Repository $($repo.name) is empty."
            } else {
                Write-Warning "Error fetching commit for repository: $($repo.name). Error: $($_.Exception.Message)"
            }
        }

        # Extract repository details
        $repoAdminAccess = $repo.permissions.admin
        $creationDate = $repo.created_at
        $creator = $repo.owner.login
        $isArchived = $repo.archived
        $repoSize = $repo.size
        $openIssues = $repo.open_issues_count
        $language = $repo.language
        $license = if ($repo.license) { $repo.license.name } else { "None" }
        $visibility = if ($repo.private) { "Private" } else { "Public" }
        $stars = $repo.stargazers_count
        $forks = $repo.forks_count
        $watches = $repo.watchers_count

        # Calculate the Alarm variable
        $currentDate = Get-Date
        $daysSinceLastCommit = ($currentDate - [datetime]$commitDate).Days
        $alarm = if ($daysSinceLastCommit -ge 90) { "TRUE" } else { "FALSE" }

        # Write the details to the CSV file
        "$($repo.name),$commitDate,$committer,$repoAdminAccess,$creationDate,$creator,$isArchived,$repoSize,$openIssues,$openPRs,$language,$license,$visibility,$stars,$forks,$watches,$alarm" | Out-File $outputFile -Append
    }

    # Check for the next page URL in the response headers
    $linkHeader = ($repos.Headers.Link -split ",") | Where-Object { $_ -like '*rel="next"*' }
    if ($linkHeader) {
        $endpoint = ($linkHeader -split ";")[0] -replace "[<>]", ""
    } else {
        $endpoint = $null
    }
} while ($endpoint)

Write-Output "Results saved to $outputFile"

