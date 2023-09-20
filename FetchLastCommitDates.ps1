$orgName = "SKY-UK"  
$outputFile = "repos_last_commit_dates.csv"

# Initialize the first API endpoint
$endpoint = "https://api.github.com/orgs/$orgName/repos?per_page=100"

# Create a new CSV file and write the headers
"Repository,Last Commit Date" | Out-File $outputFile

do {
    # Fetch a page of repositories
    $response = gh api --paginate -X GET $endpoint | ConvertFrom-Json
    foreach ($repo in $response) {
        # Try fetching the last commit date from the main branch
        $commitData = gh api repos/$orgName/$($repo.name)/commits/main 2>&1

        # Check if the repository is empty or if the main branch doesn't exist
        if ($commitData -like "*repository is empty (HTTP 409)*") {
            "$($repo.name),Repository is empty" | Out-File $outputFile -Append
            continue
        } elseif ($commitData -like "*No Commit found for SHA: main (HTTP 422)*") {
            # If main branch is not found or empty, try the master branch
            $commitDate = (gh api repos/$orgName/$($repo.name)/commits/master 2>$null | ConvertFrom-Json).commit.author.date
        } else {
            $commitDate = ($commitData | ConvertFrom-Json).commit.author.date
        }

        # If a commit date is found, write it to the CSV
        if ($commitDate) {
            "$($repo.name),$commitDate" | Out-File $outputFile -Append
        } else {
            "$($repo.name),No commits found" | Out-File $outputFile -Append
        }
    }

    # Check for the next page URL in the JSON output
    $endpoint = $response.next_page_url

    # Sleep for a short duration to avoid hitting rate limits (optional but recommended)
    Start-Sleep -Seconds 5

} while ($endpoint -and $endpoint -ne "null")

Write-Output "Results saved to $outputFile"
