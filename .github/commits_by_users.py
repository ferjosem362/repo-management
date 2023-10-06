# Define the organization name
$orgName = "SKY-UK"

# Define the base API URL
$baseUrl = "https://api.github.com/orgs/$orgName"

# Define headers for the API request
$headers = @{
    "Accept" = "application/vnd.github.v3+json"
    "Authorization" = "token XGrbmKndIAlTJvP2X2CZdIB6HKK+WOSwlWA5V1Jm5a4" # Replace with your PAT
}

# Initialize an empty array to store the results
$results = @()

# Fetch all repositories for the organization
$repos = Invoke-RestMethod -Uri "$baseUrl/repos" -Headers $headers

# Loop through each repository
foreach ($repo in $repos) {
    # Check for repositories with no titles
    if (-not $repo.name) {
        $results += [PSCustomObject]@{
            "Repository"   = "<No Title>"
            "LastCommitDate" = "<N/A>"
            "Committer"    = "<N/A>"
        }
        continue
    }

    # Fetch the last commit for the repository
    try {
        $lastCommit = Invoke-RestMethod -Uri $repo.commits_url.Replace("{/sha}", "") -Headers $headers | Select-Object -First 1

        # If there's a last commit, fetch the user who made the commit and the date
        if ($lastCommit) {
            $commitDate = $lastCommit.commit.author.date
            $committer = $lastCommit.commit.author.name
        } else {
            $commitDate = "<Never Committed>"
            $committer = "<N/A>"
        }
    } catch {
        $commitDate = "<Error Fetching Commit>"
        $committer = "<Error Fetching Committer>"
    }

    # Add the repo name, commit date, and committer to the results array
    $results += [PSCustomObject]@{
        "Repository"   = $repo.name
        "LastCommitDate" = $commitDate
        "Committer"    = $committer
    }
}

# Display the results
$results | Format-Table -AutoSize

# Export the results to a CSV file
$results | Export-Csv -Path "repos_with_commits.csv" -NoTypeInformation
