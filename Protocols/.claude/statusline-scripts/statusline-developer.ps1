# Developer StatusLine - Time, Model, User, and Git Branch
# Balanced view with essential developer information

$jsonInput = [Console]::In.ReadToEnd()
$data = $jsonInput | ConvertFrom-Json

$time = Get-Date -Format 'hh:mmtt'
$model = if ($data.model.display_name) { $data.model.display_name } else { 'Claude' }
$branch = git branch --show-current 2>$null
if (-not $branch) { $branch = 'main' }

Write-Output "$time | $model | $env:USERNAME [GitBranch: $branch]"
