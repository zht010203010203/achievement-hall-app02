@echo off
chcp 65001 >nul
echo ======================================
echo   成就殿堂 - APK 打包工具
echo ======================================
echo.

REM 检查 WSL 是否安装
wsl --list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到 WSL2
    echo.
    echo 请先安装 WSL2：
    echo 1. 以管理员身份运行 PowerShell
    echo 2. 执行：wsl --install -d Ubuntu
    echo 3. 重启电脑
    echo 4. 再次运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✅ 检测到 WSL2
echo.

echo 请选择操作：
echo 1) 复制项目到 WSL 并开始打包
echo 2) 仅打开 WSL 终端
echo 3) 查看打包指南
echo 4) 退出
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" (
    echo.
    echo ======================================
    echo   准备打包环境
    echo ======================================
    echo.

    REM 获取当前目录
    set "current_dir=%cd%"

    echo 正在复制项目到 WSL...
    wsl bash -c "mkdir -p ~/achievementhall"
    wsl bash -c "cp -r /mnt/d/OneDrive/桌面/文件/程序/刷题app/* ~/achievementhall/ 2>/dev/null || cp -r '%current_dir:\=/%'/* ~/achievementhall/"

    echo ✅ 项目已复制到 ~/achievementhall
    echo.
    echo 正在启动 WSL 打包脚本...
    wsl bash -c "cd ~/achievementhall && chmod +x build_apk.sh && ./build_apk.sh"

) else if "%choice%"=="2" (
    echo.
    echo 打开 WSL 终端...
    echo 提示：项目位于 ~/achievementhall 目录
    echo.
    wsl bash -c "cd ~/achievementhall 2>/dev/null || cd ~; exec bash"

) else if "%choice%"=="3" (
    echo.
    start "" "APK打包指南.md"
    echo ✅ 已打开打包指南
    pause

) else if "%choice%"=="4" (
    echo 退出
    exit /b 0

) else (
    echo 无效选项
    pause
    exit /b 1
)

echo.
echo ======================================
echo   完成！
echo ======================================
echo.

REM 询问是否传输 APK 到电脑
if exist "\\wsl$\Ubuntu\home\%username%\achievementhall\bin\*.apk" (
    echo 检测到已生成的 APK 文件
    set /p copy="是否复制到当前目录？(y/n): "
    if /i "%copy%"=="y" (
        mkdir ".\apk" 2>nul
        copy "\\wsl$\Ubuntu\home\%username%\achievementhall\bin\*.apk" ".\apk\" >nul
        echo ✅ APK 已复制到 .\apk\ 目录
        explorer ".\apk"
    )
)

pause
