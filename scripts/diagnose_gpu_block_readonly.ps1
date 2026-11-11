# CacheNorth - read-only diagnostic for "koboldcpp-launcher.exe - Bad Image" (0xc0e90002).
# Run in a normal (non-admin) PowerShell window on the affected computer. Changes nothing.
$ErrorActionPreference = "SilentlyContinue"
$cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
"Windows: $($cv.ProductName) $($cv.DisplayVersion) build $($cv.CurrentBuild).$($cv.UBR)"
"CPU: $((Get-CimInstance Win32_Processor).Name)"
"GPU: $((Get-CimInstance Win32_VideoController | ForEach-Object Name) -join '; ')"
$sacReg = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy').VerifiedAndReputablePolicyState
$sac = @{0 = 'Off'; 1 = 'On (enforcing)'; 2 = 'Evaluation'}[[int]$sacReg]
"Smart App Control (registry): $(if ($null -eq $sacReg) { 'not present' } else { $sac })"
"Smart App Control (Defender): $((Get-MpComputerStatus).SmartAppControlState)"
""
"Code Integrity events mentioning KoboldCpp (newest first, last 30 days):"
$events = Get-WinEvent -FilterHashtable @{ LogName = 'Microsoft-Windows-CodeIntegrity/Operational'; StartTime = (Get-Date).AddDays(-30) } -MaxEvents 5000 |
    Where-Object { $_.Message -match 'kobold' }
if (-not $events) { "  none found" }
$events | Select-Object -First 20 | ForEach-Object {
    $first = ($_.Message -split "`r?`n")[0]
    "  {0:yyyy-MM-dd HH:mm:ss}  Event {1}  {2}" -f $_.TimeCreated, $_.Id, $first.Substring(0, [Math]::Min(220, $first.Length))
}
""
"Event 3077/3033 = file blocked by policy (enforced). 3076/3034 = audit only (would have been blocked)."
"Policy names containing 'VerifiedAndReputable' or 'Smart App Control' identify Smart App Control."
