@echo off
chcp 65001 >nul
set "SCRIPT_DIR=%~dp0"
set "SHORTCUT=%USERPROFILE%\Desktop\邮箱管家.lnk"
set "TARGET=%SCRIPT_DIR%启动邮箱管家.vbs"
set "ICON=%SCRIPT_DIR%icon.ico"

REM 检查是否有自定义图标
if exist "%ICON%" (
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%ICON%'; $s.Description = '邮箱管家 - 批量邮箱管理工具'; $s.Save()"
) else (
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = 'shell32.dll,156'; $s.Description = '邮箱管家 - 批量邮箱管理工具'; $s.Save()"
)

echo 桌面快捷方式已创建！
pause
