# 上传到GitHub和HuggingFace的脚本

Write-Host "========================================" -ForegroundColor Green
Write-Host "   岐黄AI - 上传到GitHub和HuggingFace" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查git是否安装
$gitVersion = git --version 2>$null
if (-not $gitVersion) {
    Write-Host "[错误] 未安装Git，请先安装Git" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/downloads" -ForegroundColor Yellow
    exit 1
}

# 检查huggingface-cli是否安装
$hfCli = huggingface-cli --version 2>$null
if (-not $hfCli) {
    Write-Host "[警告] 未安装huggingface_hub，正在安装..." -ForegroundColor Yellow
    pip install huggingface_hub
}

Write-Host ""
Write-Host "请输入以下信息:" -ForegroundColor Cyan
Write-Host ""

# 获取GitHub用户名
$githubUsername = Read-Host "GitHub用户名"
if (-not $githubUsername) {
    Write-Host "[错误] GitHub用户名不能为空" -ForegroundColor Red
    exit 1
}

# 获取HuggingFace用户名
$hfUsername = Read-Host "HuggingFace用户名 (默认同GitHub)"
if (-not $hfUsername) {
    $hfUsername = $githubUsername
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   步骤1: 初始化Git仓库" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 检查是否已经是git仓库
if (Test-Path ".git") {
    Write-Host "[信息] Git仓库已存在" -ForegroundColor Yellow
} else {
    Write-Host "[执行] git init" -ForegroundColor Cyan
    git init
    git branch -M main
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   步骤2: 添加远程仓库" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 添加GitHub远程仓库
$githubRepo = "https://github.com/$githubUsername/qihuang-ai.git"
Write-Host "[执行] git remote add origin $githubRepo" -ForegroundColor Cyan
git remote remove origin 2>$null
git remote add origin $githubRepo

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   步骤3: 提交代码到GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "[执行] git add ." -ForegroundColor Cyan
git add .

Write-Host "[执行] git commit" -ForegroundColor Cyan
git commit -m "Initial commit: 岐黄AI智能中医诊断系统"

Write-Host "[执行] git push" -ForegroundColor Cyan
Write-Host ""
Write-Host "请输入GitHub用户名和密码（或Personal Access Token）" -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "[成功] 代码已上传到GitHub!" -ForegroundColor Green
    Write-Host "GitHub仓库地址: https://github.com/$githubUsername/qihuang-ai" -ForegroundColor Cyan
} else {
    Write-Host "[错误] GitHub上传失败，请检查用户名和密码" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   步骤4: 上传模型到HuggingFace" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "请先登录HuggingFace:" -ForegroundColor Yellow
Write-Host "1. 访问 https://huggingface.co/settings/tokens" -ForegroundColor Yellow
Write-Host "2. 创建一个Access Token" -ForegroundColor Yellow
Write-Host "3. 运行: huggingface-cli login" -ForegroundColor Yellow
Write-Host ""

$login = Read-Host "是否已登录HuggingFace? (y/n)"
if ($login -eq "y") {
    # 创建HuggingFace模型仓库目录
    $hfDir = "huggingface_model"
    if (Test-Path $hfDir) {
        Remove-Item -Recurse -Force $hfDir
    }
    New-Item -ItemType Directory -Path $hfDir | Out-Null
    
    # 复制模型文件
    Write-Host "[复制] 模型文件..." -ForegroundColor Cyan
    Copy-Item "training\checkpoints\best_model.pt" $hfDir
    Copy-Item "training\checkpoints\README.md" $hfDir
    Copy-Item "data\chatmed\meta.json" $hfDir
    
    # 创建HuggingFace README
    $hfReadme = @"
---
license: mit
language:
- zh
tags:
- chinese-medicine
- tcm
- diagnosis
- pytorch
- lsan
---

# 岐黄AI - 中医诊断模型

## 模型信息

| 指标 | 数值 |
|------|------|
| 模型架构 | LSAN (Label-Specific Attention Network) |
| 训练样本 | 54,204 条 |
| 症状种类 | 9,629 种 |
| 中药种类 | 273 种 |
| 测试集F1 | 0.386 |

## 使用方法

```python
from huggingface_hub import hf_hub_download

# 下载模型
model_path = hf_hub_download(
    repo_id="$hfUsername/qihuang-ai-model",
    filename="best_model.pt"
)
```

## 相关项目

- [GitHub仓库](https://github.com/$githubUsername/qihuang-ai)

## 许可证

MIT License

## 免责声明

本模型仅供学习研究使用，不用于实际医疗诊断。
"@
    
    Set-Content -Path "$hfDir\README.md" -Value $hfReadme -Encoding UTF8
    
    # 上传到HuggingFace
    Write-Host "[执行] 上传到HuggingFace..." -ForegroundColor Cyan
    
    Push-Location $hfDir
    huggingface-cli repo create qihuang-ai-model --type model --organization $hfUsername
    git init
    git branch -M main
    git remote add origin "https://huggingface.co/$hfUsername/qihuang-ai-model"
    git add .
    git commit -m "Upload model"
    git push -u origin main
    Pop-Location
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[成功] 模型已上传到HuggingFace!" -ForegroundColor Green
        Write-Host "HuggingFace模型地址: https://huggingface.co/$hfUsername/qihuang-ai-model" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   上传完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "GitHub仓库: https://github.com/$githubUsername/qihuang-ai" -ForegroundColor Cyan
Write-Host "HuggingFace模型: https://huggingface.co/$hfUsername/qihuang-ai-model" -ForegroundColor Cyan
Write-Host ""
