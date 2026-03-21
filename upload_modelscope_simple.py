"""
上传模型到ModelScope - 简化版
运行方式: python upload_modelscope_simple.py YOUR_TOKEN YOUR_USERNAME
"""
from modelscope.hub.api import HubApi
import os
import sys

def main():
    if len(sys.argv) < 3:
        print("使用方法: python upload_modelscope_simple.py <TOKEN> <USERNAME>")
        print()
        print("获取Token: https://modelscope.cn/my/myaccesstoken")
        print("示例: python upload_modelscope_simple.py abc123def456 myusername")
        return

    token = sys.argv[1]
    username = sys.argv[2]

    print("=" * 50)
    print("   上传模型到ModelScope")
    print("=" * 50)
    print()

    # 登录
    api = HubApi()
    api.login(token)
    print(f"✓ 登录成功! 用户: {username}")

    model_id = f"{username}/qihuang-ai-model"
    print(f"✓ 目标仓库: {model_id}")
    print()

    # 要上传的文件
    files = [
        ("training/checkpoints/best_model.pt", "best_model.pt"),
        ("data/chatmed/meta.json", "meta.json"),
    ]

    for local_path, remote_name in files:
        if os.path.exists(local_path):
            size_mb = os.path.getsize(local_path) / 1024 / 1024
            print(f"上传: {local_path} ({size_mb:.2f} MB)")
            try:
                api.push_model(
                    model_id=model_id,
                    model_dir=os.path.dirname(local_path) or ".",
                    commit_message=f"Upload {remote_name}"
                )
                print(f"✓ {remote_name} 上传成功!")
            except Exception as e:
                print(f"✗ 上传失败: {e}")
        else:
            print(f"✗ 文件不存在: {local_path}")

    print()
    print("=" * 50)
    print("上传完成!")
    print(f"模型地址: https://modelscope.cn/models/{model_id}")
    print("=" * 50)


if __name__ == "__main__":
    main()