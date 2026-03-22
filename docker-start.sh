#!/bin/bash
# Docker部署脚本

echo "=================================="
echo "   岐黄AI Docker部署"
echo "=================================="
echo ""

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: docker-compose未安装，请先安装docker-compose"
    exit 1
fi

# 检查模型文件
if [ ! -f "training/checkpoints/best_model.pt" ]; then
    echo "警告: 模型文件不存在，正在下载..."
    echo "请手动下载模型到 training/checkpoints/best_model.pt"
    echo ""
    echo "下载方式:"
    echo "  from modelscope import snapshot_download"
    echo "  snapshot_download('cy1750/qihuang-ai-model', cache_dir='./training/checkpoints')"
    exit 1
fi

echo "开始构建Docker镜像..."
docker-compose build

echo ""
echo "启动服务..."
docker-compose up -d

echo ""
echo "=================================="
echo "   部署完成!"
echo "=================================="
echo ""
echo "访问地址:"
echo "  前端: http://localhost:3000"
echo "  后端: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "停止服务: docker-compose down"
echo "查看日志: docker-compose logs -f"
echo ""