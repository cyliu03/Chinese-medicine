#!/usr/bin/env python3
"""
岐黄AI - 一键上传脚本
自动上传代码到GitHub和模型到HuggingFace
"""

import subprocess
import sys
import os
from pathlib import Path

def run_cmd(cmd, check=True):
    """运行命令"""
    print(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"错误: {result.stderr}")
    return result

def upload_github(token):
    """上传到GitHub"""
    print("\n" + "="*50)
    print("上传代码到 GitHub")
    print("="*50)
    
    # 配置git
    run_cmd('git config user.email "cyliu03@users.noreply.github.com"')
    run_cmd('git config user.name "cyliu03"')
    
    # 设置远程URL
    repo_url = f"https://{token}@github.com/cyliu03/Chinese-medicine.git"
    run_cmd(f'git remote set-url origin {repo_url}')
    
    # 添加文件
    run_cmd('git add -A')
    
    # 提交
    run_cmd('git commit -m "feat: 岐黄AI智能中医诊断系统完整实现"')
    
    # 推送
    result = run_cmd('git push -u origin master --force')
    
    if result.returncode == 0:
        print("\n✅ GitHub上传成功!")
        print("https://github.com/cyliu03/Chinese-medicine")
        return True
    return False

def upload_huggingface(token):
    """上传到HuggingFace"""
    print("\n" + "="*50)
    print("上传模型到 HuggingFace")
    print("="*50)
    
    try:
        from huggingface_hub import HfApi, create_repo, login
        
        # 登录
        login(token=token)
        api = HfApi()
        
        # 获取用户名
        user = api.whoami(token)
        username = user['name']
        print(f"登录用户: {username}")
        
        # 创建仓库
        repo_id = f"{username}/qihuang-ai-model"
        try:
            create_repo(repo_id=repo_id, repo_type="model", token=token, exist_ok=True)
        except:
            pass
        
        # 上传模型
        model_path = Path("models/best_model.pt")
        if model_path.exists():
            print(f"上传模型: {model_path}")
            api.upload_file(
                path_or_fileobj=str(model_path),
                path_in_repo="best_model.pt",
                repo_id=repo_id,
                repo_type="model",
                token=token
            )
            print("✅ 模型上传成功!")
        
        # 上传配置文件
        configs = [
            ("models/config.json", "config.json"),
            ("models/symptom_vocab.json", "symptom_vocab.json"),
            ("models/herb_vocab.json", "herb_vocab.json"),
        ]
        for local, remote in configs:
            if Path(local).exists():
                api.upload_file(
                    path_or_fileobj=local,
                    path_in_repo=remote,
                    repo_id=repo_id,
                    repo_type="model",
                    token=token
                )
                print(f"✅ 上传: {local}")
        
        print(f"\n✅ HuggingFace上传成功!")
        print(f"https://huggingface.co/{repo_id}")
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("="*50)
    print("岐黄AI - 一键上传工具")
    print("="*50)
    
    print("\n请输入Token (直接回车跳过):")
    
    gh_token = input("GitHub Token: ").strip()
    hf_token = input("HuggingFace Token: ").strip()
    
    if gh_token:
        upload_github(gh_token)
    else:
        print("\n跳过GitHub上传")
        print("获取Token: https://github.com/settings/tokens/new")
    
    if hf_token:
        upload_huggingface(hf_token)
    else:
        print("\n跳过HuggingFace上传")
        print("获取Token: https://huggingface.co/settings/tokens")
    
    print("\n完成!")

if __name__ == "__main__":
    main()
