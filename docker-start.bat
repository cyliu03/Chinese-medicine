@echo off
chcp 65001 >nul
echo ==================================
echo    岐黄AI Docker部署
echo ==================================
echo.

:: 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

:: 检查模型文件
if not exist "training\checkpoints\best_model.pt" (
    echo 警告: 模型文件不存在！
    echo 请先下载模型到 training\checkpoints\best_model.pt
    echo.
    echo 下载方式:
    echo   from modelscope import snapshot_download
    echo   snapshot_download('cy1750/qihuang-ai-model')
    pause
    exit /b 1
)

echo 开始构建Docker镜像...
docker-compose build

echo.
echo 启动服务...
docker-compose up -d

echo.
echo ==================================
echo    部署完成!
echo ==================================
echo.
echo 访问地址:
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo 停止服务: docker-compose down
echo 查看日志: docker-compose logs -f
echo.
pause