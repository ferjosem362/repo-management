$orgName = "SKY-UK"  # Replace with your organization's name
$outputFile = "detailed_repos_info.csv"

# Create a new CSV file and write the headers
"Repository,Last Commit Date,Committer,Repo Admin Access,Creation Date,Creator,Is Archived,Repo Size (KB)" | Out-File $outputFile

# Fetch all repositories for the organization
$repos = $null
try {
    $repos = gh api --paginate -X GET "orgs/$orgName/repos?per_page=100" | ConvertFrom-Json
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
        $commitInfo = gh api "repos/$orgName/$($repo.name)/commits/main" | ConvertFrom-Json
        $commitDate = $commitInfo.commit.author.date
        $committer = $commitInfo.commit.author.name
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

    # Write the details to the CSV file
    "$($repo.name),$commitDate,$committer,$repoAdminAccess,$creationDate,$creator,$isArchived,$repoSize" | Out-File $outputFile -Append
}

Write-Output "Results saved to $outputFile"
