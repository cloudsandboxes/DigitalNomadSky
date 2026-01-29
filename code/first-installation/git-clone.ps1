$GithubRepoUrl = "https://github.com/cloudsandboxes/nomadsky.git"
$CloneDirectory = "C:\Projects"
$repoName = ($GithubRepoUrl -split '/')[-1] -replace '\.git$', ''
$repoPath = Join-Path $CloneDirectory $repoName
git clone $GithubRepoUrl $repoPath
