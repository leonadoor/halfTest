$TaskName = "AI-News-Daily-Digest"
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = if ($env:PYTHON_EXE) { $env:PYTHON_EXE } else { "python" }
$Arguments = "`"$ScriptRoot\run_scheduled_job.py`""

$Action = New-ScheduledTaskAction `
  -Execute $PythonExe `
  -Argument $Arguments `
  -WorkingDirectory $ScriptRoot

$Trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
$Settings = New-ScheduledTaskSettingsSet `
  -MultipleInstances IgnoreNew `
  -StartWhenAvailable `
  -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask `
  -TaskName $TaskName `
  -Action $Action `
  -Trigger $Trigger `
  -Settings $Settings `
  -Description "Run the AI News Aggregator every day and persist scheduler logs." `
  -Force
