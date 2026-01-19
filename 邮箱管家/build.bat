@echo off
chcp 65001
echo 正在打包邮箱管家...

REM 安装依赖
pip install -r requirements.txt

REM 打包为exe
pyinstaller --noconfirm --onefile --windowed ^
    --name "邮箱管家" ^
    --add-data "ui;ui" ^
    --add-data "core;core" ^
    --add-data "database;database" ^
    --hidden-import "PyQt5.sip" ^
    --hidden-import "IMAPClient" ^
    main.py

echo 打包完成！
echo 可执行文件位于 dist 文件夹
pause
