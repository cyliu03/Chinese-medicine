@echo off
chcp 65001

echo ========================================
echo    岐黄AI 智能中医诊断系统 - 启动脚本
echo ========================================
echo.

REM 设置代码页编码为UTF-8
chcp 65001 >nul 2>&1

REM 设置Python环境
set PYTHONIO_INPUT_ENCODING=utf-8
set PYTHONUTF8=on
set PYTHONLEGACY_WINDOWSIOENCODING=UTF-8

REM 检查是否在正确的目录
cd /d "%~dp0%" || cd /d

REM 激活虚拟环境
call venv\Scripts\activate.bat >nul 2>&1

REM 设置API端口
set MODEL_API_URL=http://localhost:8000

REM 启动后端服务
echo [后端] 启动后端服务...
start /B cmd /k "cd /d "%~dp0%" && "start /B cmd /k" python main.py"
echo 后端服务启动在 http://localhost:8000

REM 磀查后端是否启动成功
:check_backend
if error goto :handle_error

)

REM 磀查前端是否已构建
if not exist ".next" (
    echo [前端] 构建前端...
    call npm run build
    if error goto :handle_error
)

REM 启动前端服务
echo [前端] 启动前端服务...
start /B cmd /k "npm start"
echo 前端服务启动在 http://localhost:3000

REM 检查前端是否启动成功
:check_frontend
if error goto :handle_error
)

REM 磀查后端是否启动成功
:check_backend
if error goto :handle_error
)

REM 磀查前端是否启动成功
:check_frontend
if error goto :handle_error
)

echo.
echo ========================================
echo    服务启动完成！
echo ========================================
echo.
echo 访问地址:
echo   傣者端: http://localhost:3000/patient
echo   医生端: http://localhost:3000/doctor
echo.
echo 按 Ctrl+C 建所有服务
echo.

:handle_error
echo.
echo [错误] 发生错误，pause
