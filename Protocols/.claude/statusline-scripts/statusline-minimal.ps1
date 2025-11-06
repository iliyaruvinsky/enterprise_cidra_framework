# Minimal StatusLine - Time and Model only
# Simple, clean view for focused work sessions

$jsonInput = [Console]::In.ReadToEnd()
$data = $jsonInput | ConvertFrom-Json

$time = Get-Date -Format 'hh:mmtt'
$model = if ($data.model.display_name) { $data.model.display_name } else { 'Claude' }

Write-Output "$time | $model"
