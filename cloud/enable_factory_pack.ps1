# Enables the Industrial Factory resource pack zips in the Diaithir client's options.txt.
# Run with Minecraft CLOSED (it rewrites options.txt on exit and would undo this).
# Reads the zip names that really exist in resourcepacks, so it works for "IF1.zip" and "Industrial Factory 1.zip" alike.
$mc = "E:\Prism\instances\Diaithir\.minecraft"
$opt = Join-Path $mc "options.txt"
$dir = Join-Path $mc "resourcepacks"
if (Get-Process -Name javaw,java -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*Minecraft*" }) { Write-Host "Close Minecraft first."; exit 1 }
$zips = Get-ChildItem $dir -Filter *.zip | Where-Object { $_.Name -match '^(IF|Industrial Factory ?)(\d+)\.zip$' } |
        Sort-Object { [int]([regex]::Match($_.Name,'(\d+)\.zip$').Groups[1].Value) }
if (-not $zips) { Write-Host "No Industrial Factory zips found in $dir"; exit 1 }
$ids = @('vanilla','mod_resources') + @($zips | ForEach-Object { 'file/' + $_.Name })
$sounds = Get-ChildItem $dir -Filter 'diaithir-sounds.zip' -ErrorAction SilentlyContinue
if ($sounds) { $ids += 'file/diaithir-sounds.zip' }
$json = '[' + (($ids | ForEach-Object { '"' + $_ + '"' }) -join ',') + ']'
$lines = Get-Content $opt
$found = $false
$out = foreach ($l in $lines) { if ($l -like 'resourcePacks:*') { $found = $true; "resourcePacks:$json" } elseif ($l -like 'incompatibleResourcePacks:*') { 'incompatibleResourcePacks:[]' } else { $l } }
if (-not $found) { $out = @($out) + "resourcePacks:$json" }
Copy-Item $opt "$opt.bak_before_factory" -Force
Set-Content -Path $opt -Value $out -Encoding ASCII
Write-Host "Enabled $($zips.Count) pack zips. resourcePacks line:"
Write-Host "resourcePacks:$json"
