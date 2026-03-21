#!/usr/bin/env python3
"""
岐黄AI - GitHub和HuggingFace上传脚本
使用方法: python upload_all.py --github-token YOUR_TOKEN --hf-token YOUR_TOKEN
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并返回结果"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    else:
        print(f"成功: {result.stdout}")
    return result.returncode == 0

def setup_git_config():
    """配置Git用户信息"""
    print("\n=== 配置Git ===")
    run_command('git config user.email "cyliu03@users.noreply.github.com"')
    run_command('git config user.name "cyliu03"')

def upload_to_github(token):
    """上传代码到GitHub"""
    print("\n=== 上传到GitHub ===")
    
    # 设置远程URL带token
    repo_url = f"https://{token}@github.com/cyliu03/Chinese-medicine.git"
    run_command(f'git remote set-url origin {repo_url}')
    
    # 添加所有文件
    print("添加文件到暂存区...")
    run_command('git add -A')
    
    # 查看状态
    run_command('git status')
    
    # 提交
    print("提交更改...")
    run_command('git commit -m "feat: 岐黄AI智能中医诊断系统 - 完整前端重设计"')
    
    # 推送
    print("推送到GitHub...")
    result = run_command('git push -u origin master --force')
    
    if result:
        print("✅ GitHub上传成功!")
        print("仓库地址: https://github.com/cyliu03/Chinese-medicine")
    else:
        print("❌ GitHub上传失败，请检查Token权限")
    
    return result

def upload_to_huggingface(token):
    """上传模型到HuggingFace"""
    print("\n=== 上传到HuggingFace ===")
    
    try:
        from huggingface_hub import HfApi, create_repo, login
        
        # 登录
        login(token=token)
        
        api = HfApi()
        
        # 获取用户信息
        user_info = api.whoami(token)
        username = user_info['name']
        print(f"登录用户: {username}")
        
        # 创建仓库
        repo_id = f"{username}/qihuang-ai-model"
        print(f"创建仓库: {repo_id}")
        
        try:
            create_repo(
                repo_id=repo_id,
                repo_type="model",
                token=token,
                exist_ok=True
            )
        except Exception as e:
            print(f"仓库已存在或创建失败: {e}")
        
        # 上传模型文件
        model_path = Path("models/best_model.pt")
        if model_path.exists():
            print(f"上传模型文件: {model_path}")
            api.upload_file(
                path_or_fileobj=str(model_path),
                path_in_repo="best_model.pt",
                repo_id=repo_id,
                repo_type="model",
                token=token
            )
            print("✅ 模型文件上传成功!")
        else:
            print(f"⚠️ 模型文件不存在: {model_path}")
        
        # 上传配置文件
        config_files = [
            ("models/config.json", "config.json"),
            ("models/symptom_vocab.json", "symptom_vocab.json"),
            ("models/herb_vocab.json", "herb_vocab.json"),
        ]
        
        for local_path, remote_path in config_files:
            if Path(local_path).exists():
                print(f"上传配置文件: {local_path}")
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=remote_path,
                    repo_id=repo_id,
                    repo_type="model",
                    token=token
                )
        
        # 上传README
        readme_content = """---
license: mit
language:
- zh
tags:
- tcm
- chinese-medicine
- diagnosis
- multi-label-classification
---

# 岐黄AI - 中医智能诊断模型

## 模型简介

基于LSAN (Label-Specific Attention Network) 的中医智能诊断模型，用于根据症状预测中药处方。

## 模型详情

- **架构**: LSAN (Label-Specific Attention Network)
- **任务**: 多标签分类 (症状 → 中药)
- **训练数据**: ChatMed_TCM (54,204样本)
- **症状数量**: 9,629种
- **中药数量**: 273种
- **性能**: F1 = 0.386

## 使用方法

```python
import torch
from models.lsan_model import LSAN

# 加载模型
model = LSAN(
    vocab_size=9629,
    num_labels=273,
    embed_dim=256,
    hidden_dim=512
)
model.load_state_dict(torch.load('best_model.pt'))
model.eval()

# 预测
symptoms = torch.tensor([[1, 5, 23, 156]])  # 症状索引
with torch.no_grad():
    predictions = model(symptoms)
    predicted_herbs = (predictions > 0.5).nonzero()
```

## 文件说明

- `best_model.pt` - 模型权重
- `config.json` - 模型配置
- `symptom_vocab.json` - 症状词表
- `herb_vocab.json` - 中药词表

## 项目地址

- GitHub: https://github.com/cyliu03/Chinese-medicine
"""
        
        # 写入临时README
        temp_readme = Path("temp_readme.md")
        temp_readme.write_text(readme_content, encoding='utf-8')
        
        api.upload_file(
            path_or_fileobj=str(temp_readme),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            token=token
        )
        
        temp_readme.unlink()
        
        print(f"\n✅ HuggingFace上传成功!")
        print(f"模型地址: https://huggingface.co/{repo_id}")
        
        return True
        
    except ImportError:
        print("❌ 请先安装huggingface_hub: pip install huggingface_hub")
        return False
    except Exception as e:
        print(f"❌ HuggingFace上传失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='上传岐黄AI到GitHub和HuggingFace')
    parser.add_argument('--github-token', help='GitHub Personal Access Token')
    parser.add_argument('--hf-token', help='HuggingFace Token')
    parser.add_argument('--github-only', action='store_true', help='只上传到GitHub')
    parser.add_argument('--hf-only', action='store_true', help='只上传到HuggingFace')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("岐黄AI - 自动上传脚本")
    print("=" * 60)
    
    # 检查当前目录
    if not Path(".git").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 配置Git
    setup_git_config()
    
    # 上传到GitHub
    if not args.hf_only:
        if args.github_token:
            upload_to_github(args.github_token)
        else:
            print("\n⚠️ 未提供GitHub Token，跳过GitHub上传")
            print("获取Token: https://github.com/settings/tokens/new")
    
    # 上传到HuggingFace
    if not args.github_only:
        if args.hf_token:
            upload_to_huggingface(args.hf_token)
        else:
            print("\n⚠️ 未提供HuggingFace Token，跳过HuggingFace上传")
            print("获取Token: https://huggingface.co/settings/tokens")
    
    print("\n" + "=" * 60)
    print("上传完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
