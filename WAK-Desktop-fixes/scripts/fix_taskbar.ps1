Write-Host "Setting Taskbar Preferences via PowerShell..."

# Center Taskbar
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAl" -Value 1 -Force

# Always Combine (Hidden Labels)
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarGlomLevel" -Value 0 -Force
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "MMTaskbarGlomLevel" -Value 0 -Force

# Legacy + Standard Policy Cleanup
$policies = @(
    "HKCU:\Software\Policies\Microsoft\Windows\Explorer",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
)

foreach ($path in $policies) {
    if (Test-Path $path) {
        Remove-ItemProperty -Path $path -Name "TaskbarGlomLevel" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $path -Name "NoTaskGrouping" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $path -Name "LockTaskbar" -ErrorAction SilentlyContinue
        Remove-ItemProperty -Path $path -Name "TaskbarLockAll" -ErrorAction SilentlyContinue
        
        # Force NoTaskGrouping to 0 just in case
        Set-ItemProperty -Path $path -Name "NoTaskGrouping" -Value 0 -Force -ErrorAction SilentlyContinue
    }
}

# Notification (Broadcast SettingChange)
$code = @'
    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    public static extern IntPtr SendMessageTimeout(
        IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam,
        uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
'@

try {
    $win32 = Add-Type -MemberDefinition $code -Name "Win32SendMessage" -Namespace Win32 -PassThru -ErrorAction SilentlyContinue
    $null = 0
    $win32::SendMessageTimeout(0xFFFF, 0x001A, 0, "Environment", 2, 5000, [ref]$null)
    Write-Host "Broadcast sent."
}
catch {
    Write-Host "Broadcast skipped."
}

Write-Host "Taskbar settings applied to registry. Changes apply on next Login/Explorer restart."
