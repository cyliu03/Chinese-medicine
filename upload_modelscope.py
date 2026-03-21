"""
上传模型到ModelScope（魔搭社区）
国内用户推荐使用此方式下载模型
"""
from modelscope.hub.api import HubApi
from modelscope.hub.file_download import model_file_download
import os

def upload_to_modelscope():
    """
    上传模型到ModelScope

    使用前需要:
    1. 注册ModelScope账号: https://modelscope.cn/
    2. 获取SDK Token: https://modelscope.cn/my/myaccesstoken
    3. 安装modelscope: pip install modelscope
    """
    print("=" * 50)
    print("   上传模型到ModelScope（魔搭社区）")
    print("=" * 50)
    print()

    # 获取用户输入
    token = input("请输入ModelScope SDK Token (从 https://modelscope.cn/my/myaccesstoken 获取): ").strip()

    if not token:
        print("Token不能为空!")
        return

    # 初始化API
    api = HubApi()
    api.login(token)

    # 模型仓库信息
    model_id = "cyliu/qihuang-ai-model"  # 修改为你的用户名

    print(f"\n准备上传到: {model_id}")
    print()

    # 文件列表
    files_to_upload = [
        ("training/checkpoints/best_model.pt", "best_model.pt"),
        ("data/chatmed/meta.json", "meta.json"),
        ("training/checkpoints/README.md", "README.md"),
    ]

    for local_path, remote_path in files_to_upload:
        if os.path.exists(local_path):
            print(f"上传: {local_path} -> {remote_path}")
            try:
                api.push_model(
                    model_id=model_id,
                    model_dir=os.path.dirname(local_path) or ".",
                    commit_message=f"Upload {remote_path}"
                )
                print(f"✓ {remote_path} 上传成功!")
            except Exception as e:
                print(f"✗ 上传失败: {e}")
        else:
            print(f"✗ 文件不存在: {local_path}")

    print()
    print("=" * 50)
    print("上传完成!")
    print(f"ModelScope模型地址: https://modelscope.cn/models/{model_id}")
    print("=" * 50)


def download_from_modelscope():
    """从ModelScope下载模型"""
    print("=" * 50)
    print("   从ModelScope下载模型")
    print("=" * 50)

    model_id = "cyliu/qihuang-ai-model"

    # 下载模型文件
    print("\n下载模型文件...")
    model_path = model_file_download(
        model_id=model_id,
        file_path="best_model.pt",
        cache_dir="./training/checkpoints"
    )
    print(f"模型文件下载到: {model_path}")

    # 下载词汇表
    print("\n下载词汇表...")
    meta_path = model_file_download(
        model_id=model_id,
        file_path="meta.json",
        cache_dir="./data/chatmed"
    )
    print(f"词汇表下载到: {meta_path}")

    print("\n下载完成!")


if __name__ == "__main__":
    print("\n请选择操作:")
    print("1. 上传模型到ModelScope")
    print("2. 从ModelScope下载模型")

    choice = input("\n请输入选项 (1/2): ").strip()

    if choice == "1":
        upload_to_modelscope()
    elif choice == "2":
        download_from_modelscope()
    else:
        print("无效选项!")