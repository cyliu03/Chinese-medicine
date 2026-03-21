@echo off
echo ========================================
echo    岐黄AI 智能中医诊断系统 - 完整打包
echo ========================================
echo.

set VERSION=1.0.0
set PACKAGE_NAME=qihuang-ai-v%VERSION%
set BUILD_DIR=build\%PACKAGE_NAME%

echo [1/5] 清理旧文件...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%BUILD_DIR%.zip" del "%BUILD_DIR%.zip"

echo [2/5] 创建目录结构...
mkdir "%BUILD_DIR%"
mkdir "%BUILD_DIR%\server"
mkdir "%BUILD_DIR%\src"
mkdir "%BUILD_DIR%\src\app"
mkdir "%BUILD_DIR%\src\app\patient"
mkdir "%BUILD_DIR%\src\app\doctor"
mkdir "%BUILD_DIR%\src\components"
mkdir "%BUILD_DIR%\src\components\patient"
mkdir "%BUILD_DIR%\src\components\shared"
mkdir "%BUILD_DIR%\src\context"
mkdir "%BUILD_DIR%\src\data"
mkdir "%BUILD_DIR%\src\lib"
mkdir "%BUILD_DIR%\training"
mkdir "%BUILD_DIR%\training\checkpoints"
mkdir "%BUILD_DIR%\training\data"
mkdir "%BUILD_DIR%\training\data\chatmed"
mkdir "%BUILD_DIR%\docs"

echo [3/5] 复制文件...
xcopy /s /q src\app\* "%BUILD_DIR%\src\app\" >nul
xcopy /s /q src\components\* "%BUILD_DIR%\src\components\" >nul
xcopy /q src\context\* "%BUILD_DIR%\src\context\" >nul
xcopy /q src\data\* "%BUILD_DIR%\src\data\" >nul
xcopy /q src\lib\* "%BUILD_DIR%\src\lib\" >nul
xcopy /q server\*.py "%BUILD_DIR%\server\" >nul
xcopy /q server\requirements.txt "%BUILD_DIR%\server\" >nul
xcopy /q training\checkpoints\*.pt "%BUILD_DIR%\training\checkpoints\" >nul
xcopy /q training\data\chatmed\*.json "%BUILD_DIR%\training\data\chatmed\" >nul
xcopy /q docs\*.md "%BUILD_DIR%\docs\" >nul
xcopy package.json "%BUILD_DIR%\" >nul
xcopy package-lock.json "%BUILD_DIR%\" >nul
xcopy next.config.mjs "%BUILD_DIR%\" >nul
xcopy jsconfig.json "%BUILD_DIR%\" >nul
xcopy README.md "%BUILD_DIR%\" >nul
xcopy 部署指南.md "%BUILD_DIR%\" >nul
xcopy start.bat "%BUILD_DIR%\" >nul
xcopy .env.local "%BUILD_DIR%\" >nul

echo [4/5] 创建启动脚本...
(
echo @echo off
echo echo ========================================
echo echo    岐黄AI 智能中医诊断系统
echo echo ========================================
echo echo.
echo echo [1/2] 启动后端服务...
echo start /b cmd /k "cd /d %%~dp0%%\server && python main.py"
echo echo [2/2] 启动前端服务...
echo echo 请稍候，后端启动后按任意键启动前端...
echo pause
echo start /b cmd /k "cd /d %%~dp0%% && npm run dev"
echo echo.
echo echo ========================================
echo echo    服务已启动!
echo echo ========================================
echo echo.
echo echo 访问地址:
echo echo   前端: http://localhost:3000
echo echo   后端: http://localhost:8000
echo echo.
) > "%BUILD_DIR%\启动服务.bat"

echo [5/5] 压缩文件...
cd build
powershell Compress-Archive -Path "%PACKAGE_NAME%" -DestinationPath "%PACKAGE_NAME%.zip" -Force
cd ..

echo.
echo ========================================
echo    打包完成!
echo ========================================
echo.
echo 打包文件: build\%PACKAGE_NAME%.zip
echo.
echo 请将此文件发送给医生，解压后运行"启动服务.bat"即可
echo.
