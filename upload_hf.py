"""
上传模型和数据到HuggingFace
"""
from huggingface_hub import HfApi, create_repo
import os

def upload_to_huggingface(username, token):
    api = HfApi()
    
    # 创建模型仓库
    repo_id = f"{username}/qihuang-ai-model"
    
    print(f"创建HuggingFace仓库: {repo_id}")
    try:
        create_repo(repo_id=repo_id, repo_type="model", token=token, exist_ok=True)
        print(f"仓库已创建: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"创建仓库失败: {e}")
        return
    
    # 上传模型文件
    model_path = "training/checkpoints/best_model.pt"
    if os.path.exists(model_path):
        print(f"上传模型文件: {model_path}")
        api.upload_file(
            path_or_fileobj=model_path,
            path_in_repo="best_model.pt",
            repo_id=repo_id,
            repo_type="model",
            token=token,
        )
        print("模型文件上传成功!")
    else:
        print(f"模型文件不存在: {model_path}")
    
    # 上传数据文件
    meta_path = "data/chatmed/meta.json"
    if os.path.exists(meta_path):
        print(f"上传数据文件: {meta_path}")
        api.upload_file(
            path_or_fileobj=meta_path,
            path_in_repo="meta.json",
            repo_id=repo_id,
            repo_type="model",
            token=token,
        )
        print("数据文件上传成功!")
    else:
        print(f"数据文件不存在: {meta_path}")
    
    # 上传README
    readme_path = "training/checkpoints/README.md"
    if os.path.exists(readme_path):
        print(f"上传README: {readme_path}")
        api.upload_file(
            path_or_fileobj=readme_path,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            token=token,
        )
        print("README上传成功!")
    
    print(f"\n上传完成!")
    print(f"HuggingFace模型地址: https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    print("=" * 50)
    print("   上传模型到HuggingFace")
    print("=" * 50)
    print()
    
    username = input("请输入HuggingFace用户名: ").strip()
    token = input("请输入HuggingFace Token (从 https://huggingface.co/settings/tokens 获取): ").strip()
    
    if not username or not token:
        print("用户名和Token不能为空!")
        exit(1)
    
    upload_to_huggingface(username, token)
