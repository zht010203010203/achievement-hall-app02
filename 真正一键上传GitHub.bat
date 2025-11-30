@echo off
chcp 65001 >nul
echo.
echo ========================================
echo           Achievement Hall - Upload to GitHub
echo ========================================
echo.

REM Check if Git is installed
echo [1/6] Checking Git environment...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not installed
    echo Download: https://git-scm.com/downloads
    pause
    exit /b 1
)
echo OK: Git installed

REM Configure Git user info
echo [2/6] Configuring Git user information...
git config --global user.email "achievement-hall-app@example.com"
git config --global user.name "Achievement Hall App"
echo OK: Git user configured

REM Initialize Git repository
echo [3/6] Initializing Git repository...
if exist .git (
    echo OK: Git repository exists
) else (
    git init
    if errorlevel 1 (
        echo ERROR: Git initialization failed
        pause
        exit /b 1
    )
    echo OK: Git repository initialized
)

REM Add files to staging area
echo [4/6] Adding files to Git...
git add .
if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)
echo OK: Files added successfully

REM Commit changes
echo [5/6] Committing changes...
git commit -m "Initial commit: Achievement Hall App"
if errorlevel 1 (
    echo WARNING: Commit failed, trying empty commit...
    git commit --allow-empty -m "Initial commit"
    if errorlevel 1 (
        echo ERROR: Commit failed
        pause
        exit /b 1
    )
)
echo OK: Commit successful

REM Set remote repository
echo [6/6] Setting GitHub remote repository...
echo.
echo Steps to follow:
echo 1. Visit https://github.com/new to create new repository
echo 2. Repository name: achievement-hall-app
echo 3. Select Public

echo 4. Do NOT check README (we already have files)
echo 5. Click Create repository
echo 6. Copy the HTTPS address of your repository
echo.
set /p repo_url="Enter GitHub repository URL: "

if "%repo_url%"=="" (
    echo ERROR: No repository URL entered
    pause
    exit /b 1
)

echo Setting remote repository: %repo_url%
git remote add origin %repo_url%
if errorlevel 1 (
    echo ERROR: Failed to set remote repository
    pause
    exit /b 1
)
echo OK: Remote repository set successfully

REM Push code
echo [7/7] Pushing code to GitHub...
echo Uploading code, please wait...
git branch -M main
git push -u origin main
if errorlevel 1 (
    echo ERROR: Push failed, check network or authentication
    echo.
    echo Solutions:
    echo 1. Check network connection
    echo 2. Confirm GitHub credentials
    echo 3. Manual push: git push -u origin main
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Upload Complete!
echo ========================================
echo.
echo OK: Code uploaded to GitHub successfully
echo Repository: %repo_url%
echo.
echo Next Steps:
echo 1. Visit: gitpod.io/#%repo_url%
echo 2. Start cloud APK building
echo.
pause