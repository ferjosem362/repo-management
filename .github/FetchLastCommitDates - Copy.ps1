$orgName = "SKY-UK"  # Replace ORG_NAME with your organization's name

# Initialize pagination variables
$page = 1
$perPage = 1000  # Number of repositories fetched per page.

do {
    # Fetch a page of repositories
    $repos = gh repo list $orgName --limit $perPage --page $page | ForEach-Object { $_.Split()[0] }
    $repos | ForEach-Object { Write-Output $_ }

    # Increment the page number for the next loop iteration
    $page++

    # Sleep for a short duration to avoid hitting rate limits (optional but recommended)
    Start-Sleep -Seconds 5

} while ($repos.Count -eq $perPage)  # Continue looping as long as we're getting a full page of results
