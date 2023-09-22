# Define the organization name
$orgName = "SKY-UK"

# Define the base API URL
$baseUrl = "https://api.github.com/orgs/$orgName"

# Define headers for the API request
$headers = @{
    "Accept" = "application/vnd.github.v3+json"
    "Authorization" = "token " # Replace with your PAT
    "X-Github-SSO" = "required"
}

# Initialize an empty array to store the results
$results = @()

# Function to handle pagination and fetch all pages of results
function GetAllPages($url) {
    $allResults = @()
    do {
        $response = Invoke-RestMethod -Uri $url -Headers $headers
        $allResults += $response
        $url = ($response.Headers.Link -split ",") | Where-Object { $_ -like '*rel="next"*' } | ForEach-Object { ($_ -split ";")[0].Trim('<','>',' ') }
    } while ($url)
    return $allResults
}

# Fetch all repositories for the organization
$repos = GetAllPages "$baseUrl/repos"

# Loop through each repository
foreach ($repo in $repos) {
    # Fetch the last commit for the repository
    $lastCommit = Invoke-RestMethod -Uri $repo.commits_url.Replace("{/sha}", "") -Headers $headers | Select-Object -First 1

    # If there's a last commit, fetch the user who made the commit and the date
    if ($lastCommit) {
        $commitDate = $lastCommit.commit.author.date
        $committer = $lastCommit.commit.author.name

        # Fetch the teams associated with the repository
        $teams = GetAllPages $repo.teams_url

        # Extract team names
        $teamNames = $teams | ForEach-Object { $_.name } -join ', '

        # Add the repo name, commit date, committer, and team names to the results array
        $results += [PSCustomObject]@{
            "Repository"   = $repo.name
            "LastCommitDate" = $commitDate
            "Committer"    = $committer
            "Teams"        = $teamNames
        }
    }
}

# Display the results
$results | Format-Table -AutoSize

# Export the results to a CSV file
$results | Export-Csv -Path "repos_with_commits.csv" -NoTypeInformation
