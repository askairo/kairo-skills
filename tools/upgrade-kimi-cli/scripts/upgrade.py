import subprocess
import sys
import re
import json
import urllib.request
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

PACKAGE_NAME = "kimi-cli"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def get_latest_version():
    """从 PyPI API 获取最新版本，返回 (version, error)"""
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('info', {}).get('version'), None
    except Exception as e:
        return None, str(e)


def get_current_version():
    """获取当前安装的版本"""
    out, err, rc = run("kimi --version")
    if rc != 0:
        return None
    match = re.search(r'[\d.]+', out)
    return match.group(0) if match else None


def is_uv_installed():
    """检查是否通过 uv tool 安装"""
    # 检查 uv 命令是否存在
    out, err, rc = run("which uv")
    if rc != 0:
        return False
    
    # 检查 receipt 文件是否存在（更可靠的方式）
    import os
    uv_tools_dir = os.path.expanduser("~/.local/share/uv/tools/kimi-cli")
    if os.path.exists(os.path.join(uv_tools_dir, "uv-receipt.toml")):
        return True
    
    # 备用：检查 uv tool list 输出
    out, err, rc = run("uv tool list")
    if rc == 0 and PACKAGE_NAME in out:
        return True
    
    return False


def upgrade_with_uv():
    """使用 uv 升级"""
    print(f"检测到 uv 安装方式，执行 uv tool upgrade {PACKAGE_NAME} ...")
    out, err, rc = run(f"uv tool upgrade {PACKAGE_NAME}")
    print(out)
    if rc != 0:
        # uv tool upgrade 可能提示未安装，尝试 install --upgrade
        if "not installed" in err.lower():
            print("尝试重新安装...")
            out, err, rc = run(f"uv tool install --upgrade {PACKAGE_NAME}")
            print(out)
        if rc != 0:
            print(f"uv 升级失败: {err}", file=sys.stderr)
            return False
    return True


def upgrade_with_pip():
    """使用 pip 升级"""
    print(f"检测到 pip 安装方式，执行 pip install --upgrade {PACKAGE_NAME} ...")
    
    # 优先尝试 pip3
    for pip_cmd in ["pip3", "pip", "python3 -m pip", "python -m pip"]:
        out, err, rc = run(f"{pip_cmd} install --upgrade {PACKAGE_NAME}")
        print(out)
        if rc == 0:
            return True
    
    print(f"pip 升级失败", file=sys.stderr)
    return False


def main():
    # 1. 获取当前版本
    current = get_current_version()
    if current is None:
        print("无法获取当前 Kimi CLI 版本，请确认是否已安装", file=sys.stderr)
        sys.exit(1)
    print(f"当前版本: {current}")

    # 2. 获取最新版本
    latest, error = get_latest_version()
    if latest is None:
        print(f"无法获取最新版本: {error}", file=sys.stderr)
        # 尝试直接升级
        print("尝试直接升级...")
    else:
        print(f"最新版本: {latest}")
        
        # 3. 比较版本
        if current == latest:
            print("✅ 当前已经是最新版本，无需更新。")
            sys.exit(0)
        print(f"发现新版本: {latest} > {current}")

    # 4. 判断安装方式并升级
    if is_uv_installed():
        success = upgrade_with_uv()
    else:
        success = upgrade_with_pip()
    
    if not success:
        sys.exit(1)

    # 5. 验证
    new_version = get_current_version()
    if new_version:
        if latest and new_version == latest:
            print(f"✅ 升级成功！当前版本: {new_version}")
        else:
            print(f"升级完成，当前版本: {new_version}")
    else:
        print("升级后验证失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
