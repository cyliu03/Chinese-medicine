# 岐黄AI 智能中医诊断系统 - 启动脚本 (PowerShell版本)

Write-Host "========================================"
Write-Host "   岐黄AI 智能中医诊断系统 - 启动脚本"
Write-Host "========================================"
Write-Host ""

# 设置代码页编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIO_INPUT_ENCODING = "utf-8"
$env:PYTHONUTF8 = "on"
$env:PYTHONLEGACYWINDOWSIOENCODING = "utf-8"

# 设置API端口
$env:MODEL_API_URL = "http://localhost:8000"

Write-Host "[后端] 启动后端服务..." -ForegroundColor Green

# 启动后端服务
Start-Process -FilePath "python" -ArgumentList "server/main.py" -WorkingDirectory $PWD

# 等待后端启动
Start-Sleep -Seconds 3

Write-Host "[后端] 服务启动在 http://localhost:8000" -ForegroundColor Green

# 检查后端是否启动成功
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
        Write-Host "[后端] 健康检查通过" -ForegroundColor Green
    }
} catch {
    Write-Host "[后端] 等待启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "[前端] 启动前端服务..." -ForegroundColor Green

# 启动前端服务
Start-Process -FilePath "npm" -ArgumentList "start" -WorkingDirectory $PWD

Write-Host "[前端] 服务启动在 http://localhost:3000" -ForegroundColor Green

Write-Host ""
Write-Host "========================================"
Write-Host "   服务启动完成！"
Write-Host "========================================"
Write-Host ""
Write-Host "访问地址:"
Write-Host "  前端: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  后端: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止所有服务" -ForegroundColor Yellow
Write-Host ""
