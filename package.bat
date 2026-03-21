@echo off
echo ========================================
echo    岐黄AI 智能中医诊断系统 - 打包脚本
echo ========================================
echo.

REM 设置版本号
set VERSION=1.0.0
set PACKAGE_NAME=qihuang-ai-v%VERSION%

REM 创建打包目录
set BUILD_DIR=build\%PACKAGE_NAME%
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"

REM 创建目录结构
mkdir "%BUILD_DIR%"
mkdir "%BUILD_DIR%\server"
mkdir "%BUILD_DIR%\src"
mkdir "%BUILD_DIR%\src\app"
mkdir "%BUILD_DIR%\src\components"
mkdir "%BUILD_DIR%\src\components\patient"
mkdir "%BUILD_DIR%\src\components\shared"
mkdir "%BUILD_DIR%\src\context"
mkdir "%BUILD_DIR%\src\data"
mkdir "%BUILD_DIR%\src\lib"
mkdir "%BUILD_DIR%\training"
mkdir "%BUILD_DIR%\training\checkpoints"
mkdir "%BUILD_DIR%\training\data"
mkdir "%BUILD_DIR%\docs"

echo [1/4] 复制前端代码...
xcopy /s /q src\app\* "%BUILD_DIR%\src\app\" >nul
xcopy /s /q src\components\* "%BUILD_DIR%\src\components\" >nul
xcopy /s /q src\context\* "%BUILD_DIR%\src\context\" >nul
xcopy /s /q src\data\* "%BUILD_DIR%\src\data\" >nul
xcopy /s /q src\lib\* "%BUILD_DIR%\src\lib\" >nul

echo [2/4] 复制后端代码...
xcopy /s /q server\*.py "%BUILD_DIR%\server\" >nul
xcopy server\requirements.txt "%BUILD_DIR%\server\" >nul

echo [3/4] 复制训练相关文件...
xcopy /s /q training\checkpoints\* "%BUILD_DIR%\training\checkpoints\" >nul
xcopy /s /q training\data\chatmed\* "%BUILD_DIR%\training\data\" >nul

echo [4/4] 复制配置文件...
xcopy package.json "%BUILD_DIR%\" >nul
xcopy package-lock.json "%BUILD_DIR%\" >nul
xcopy next.config.mjs "%BUILD_DIR%\" >nul
xcopy jsconfig.json "%BUILD_DIR%\" >nul
xcopy start.bat "%BUILD_DIR%\" >nul
xcopy start.sh "%BUILD_DIR%\" >nul
xcopy README.md "%BUILD_DIR%\" >nul
xcopy 部署指南.md "%BUILD_DIR%\" >nul

echo [5/4] 复制文档...
xcopy /s /q docs\*.md "%BUILD_DIR%\docs\" >nul

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 打包目录: %BUILD_DIR%
echo.
echo 请将 %BUILD_DIR% 目录压缩后发送给医生
echo.
