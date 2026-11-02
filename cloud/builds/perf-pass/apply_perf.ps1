# Diaithir perf pass 1: run once with the server STOPPED (or it applies at next restart). Backs up every file it edits to *.bak-perf.
$s = "E:\DiaithirServer\server"
function Bak($p) { if (Test-Path $p) { Copy-Item $p "$p.bak-perf" -Force } }

# 1. JVM: compact object headers (-700 MB measured with the pack's server heap, no downside on Java 25)
$j = "$s\user_jvm_args.txt"; Bak $j
if (-not (Select-String -Path $j -Pattern 'UseCompactObjectHeaders' -Quiet)) { Add-Content $j "-XX:+UseCompactObjectHeaders" }

# 2. Server-only mods that are client mods (DistantHorizons etc). Moved, not deleted. The pack bundle makes this permanent.
$off = "$s\mods_disabled_perf"; New-Item -ItemType Directory -Force $off | Out-Null
foreach ($p in 'DistantHorizons','journeymap','MapFrontiers','configured-neoforge') {
  Get-ChildItem "$s\mods\$p*.jar" -ErrorAction SilentlyContinue | Move-Item -Destination $off -Force
}

# 3. ServerCore: adaptive load shedding and cheaper villagers/fluids
$c = "$s\config\servercore\config.yml"
if (Test-Path $c) { Bak $c
  $t = Get-Content $c -Raw
  $t = [regex]::Replace($t, '(?ms)(lobotomize-villagers:\s*\r?\n\s*enabled:) false', '$1 true')
  $t = [regex]::Replace($t, '(?ms)(^dynamic:\s*\r?\n\s*enabled:) false', '$1 true')
  Set-Content $c $t -NoNewline }
$o = "$s\config\servercore\optimizations.yml"
if (Test-Path $o) { Bak $o
  (Get-Content $o -Raw) -replace 'cancel-duplicate-fluid-ticks: false','cancel-duplicate-fluid-ticks: true' | Set-Content $o -NoNewline }
"perf pass 1 applied. Restart the server."
