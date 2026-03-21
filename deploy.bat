@echo off

echo ========================================
echo    岐黄AI 智能中医诊断系统 - 部署脚本
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    exit /b 1
)

REM 检查Node.js环境
node --version >nul 2>&1
if %errorlevel% neq 1 (
    echo [错误] 未找到Node.js。请先安装Node.js 18+
    exit /b 1
)

echo [信息] 环境检查通过
echo.

REM 安装后端依赖
echo [1/3] 安装后端Python依赖...
cd server
pip install -r requirements.txt
cd ..

echo [2/3] 安装前端依赖...
call npm install

echo.
echo ========================================
echo    安装完成！
echo ========================================
echo.
echo 启动方式:
echo   1. 启动后端服务:
echo      cd server ^&^& python main.py
echo.
echo   2. 启动前端服务:
echo      npm run dev ^(开发模式^)
echo      或
echo      npm run build ^&^& npm start ^(生产模式^)
echo.
echo   3. 访问系统:
echo      http://localhost:3000
echo.
