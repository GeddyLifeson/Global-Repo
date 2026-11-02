# Start the Diaithir production server detached, then its watchdog.
# Logs: E:\DiaithirServer\server.log / server.err; PID in server.pid. Runs at logon via the "Diaithir Server" task.
# Created through WMI so it is not in the caller's job object: a tool sandbox that freezes its job when the calling
# command ends would otherwise suspend every server thread (seen on the test server 2026-10-13).
$root = "E:\DiaithirServer"; $s = "$root\server"
if (Get-NetTCPConnection -LocalPort 25570 -State Listen -ErrorAction SilentlyContinue) { "already running on 25570"; exit 0 }
$rep = Get-Item "$root\watchdog_report.md" -ErrorAction SilentlyContinue
if ($rep -and (-not (Test-Path "$root\server.pid") -or $rep.LastWriteTime -gt (Get-Item "$root\server.pid").LastWriteTime)) { Get-Content $rep.FullName }
$java = "$env:USERPROFILE\curseforge\minecraft\Install\runtime\java-runtime-epsilon\windows-x64\java-runtime-epsilon\bin\java.exe"
$argsFile = [regex]::Match((Get-Content "$s\run.bat" -Raw), '@(libraries/\S+/win_args\.txt)').Groups[1].Value
$cmd = "cmd.exe /c `"`"$java`" @user_jvm_args.txt @$argsFile nogui > $root\server.log 2> $root\server.err`""
$t0 = Get-Date   # java is found by start time and win_args.txt: matching its parent pid missed it under the cmd.exe wrapper (false "did not start")
$cpid = & E:\launch_hidden.ps1 $cmd $s
$deadline = (Get-Date).AddSeconds(120)
do { Start-Sleep -Milliseconds 500
     $j = Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CreationDate -ge $t0 -and $_.CommandLine -like '*win_args.txt*' } | Select-Object -First 1 } until ($j -or (Get-Date) -gt $deadline)
if (-not $j) { throw "server java.exe did not start" }
Set-Content "$root\server.pid" $j.ProcessId
$py = (Get-Command python.exe).Source
$null = & E:\launch_hidden.ps1 "`"$py`" -I $root\server_watchdog.py $($j.ProcessId) --root $root" $root
"started PID $($j.ProcessId) with stall watchdog; diagnoses go to $root\watchdog_report.md"
