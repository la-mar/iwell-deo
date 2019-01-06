
$script_path = $MyInvocation.MyCommand.Path
$project_dir = Split-Path $script_path
$project_dir = $project_dir
Set-Location -Path $project_dir
Set-Location -Path '../'
Write-host "Current Working Directory is: $project_dir"


New-Variable -Name env_path -Value .venv/Scripts/python
New-Variable -Name main_path -Value main.py
Write-host "Virtualenv path is: $env_path"
Write-host "Working directory is:""$PWD"
Write-host "Entrypoint path is: $main_path"
& $env_path $main_path


