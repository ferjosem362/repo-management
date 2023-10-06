$orgName = "SKY-UK"  # Replace ORG_NAME with your organization's name
$outputFile = "repos_last_commit_dates.csv"

# Initialize the first API endpoint
$endpoint = "https://api.github.com/orgs/$orgName/repos?per_page=100"

# Create a new CSV file and write the headers
"Repository,Last Commit Date" | Out-File $outputFile

do {
    # Fetch a page of repositories
    $response = gh api --paginate -X GET $endpoint | ConvertFrom-Json
    foreach ($repo in $response) {
        $commitDate = (gh api repos/$orgName/$($repo.name)/commits/main | ConvertFrom-Json).commit.author.date
        "$($repo.name),$commitDate" | Out-File $outputFile -Append
    }

    # Check for the next page URL in the JSON output
    $endpoint = $response.next_page_url

    # Sleep for a short duration to avoid hitting rate limits (optional but recommended)
    Start-Sleep -Seconds 5

} while ($endpoint -and $endpoint -ne "null")

Write-Output "Results saved to $outputFile"
