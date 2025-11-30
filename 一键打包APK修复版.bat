@echo off
echo 正在准备Buildozer打包环境...
echo.

REM 切换到WSL环境并执行完整的一键打包命令
wsl -e bash -c "
cd /mnt/host/d/OneDrive/桌面/文件/程序/刷题app &&
echo '当前工作目录: $(pwd)' &&
echo '修复权限问题...' &&
chmod -R 755 /mnt/host/d/OneDrive/桌面/文件/程序/刷题app &&
echo '激活虚拟环境...' &&
source venv/bin/activate &&
echo '开始Buildozer打包...' &&
buildozer android debug
"

echo.
echo 打包完成！
pause