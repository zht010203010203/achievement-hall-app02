@echo off
echo ========================================
echo           一键上传到GitHub
echo ========================================
echo.
echo 步骤1：初始化Git仓库
git init
echo.
echo 步骤2：添加所有文件
git add .
echo.
echo 步骤3：提交更改
git commit -m "初始提交：成就殿堂应用"
echo.
echo 步骤4：连接到GitHub仓库（请先完成以下步骤）
echo.
echo 请在GitHub上创建仓库后执行以下命令：
echo git remote add origin https://github.com/你的用户名/achievement-hall-app.git
echo git branch -M main
echo git push -u origin main
echo.
echo 详细教程：
echo 1. 访问 https://github.com 注册账号
echo 2. 创建名为 achievement-hall-app 的仓库
echo 3. 复制上面的git命令并替换你的用户名
echo 4. 运行命令完成上传
echo.
pause