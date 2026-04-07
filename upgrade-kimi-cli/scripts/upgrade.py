import subprocess
import sys
import re
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def main():
    # 1. 获取当前版本
    out, err, rc = run("kimi --version")
    if rc != 0:
        print("无法获取当前 Kimi CLI 版本", file=sys.stderr)
        sys.exit(1)
    current = out.strip()
    print(f"当前版本: {current}")

    # 2. 获取最新版本
    out, err, rc = run("pip index versions kimi-code")
    if rc != 0:
        print(f"无法获取最新版本: {err}", file=sys.stderr)
        sys.exit(1)
    m = re.search(r'kimi-code \(([\d.]+)\)', out)
    if not m:
        print("无法解析最新版本号", file=sys.stderr)
        sys.exit(1)
    latest = m.group(1)
    print(f"最新版本: {latest}")

    # 3. 比较版本
    current_ver = re.search(r'[\d.]+', current)
    if current_ver and current_ver.group(0) == latest:
        print("当前已经是最新版本，无需更新。")
        sys.exit(0)

    # 4. 判断安装方式并升级
    out, err, rc = run("uv tool list")
    if rc == 0 and "kimi-code" in out:
        print("检测到 uv 安装方式，执行 uv tool upgrade kimi-code ...")
        out2, err2, rc2 = run("uv tool upgrade kimi-code")
        print(out2)
        if rc2 != 0:
            print(f"uv 升级失败: {err2}", file=sys.stderr)
            sys.exit(1)
    else:
        print("检测到 pip 安装方式，执行 pip install --upgrade kimi-code ...")
        out2, err2, rc2 = run("pip install --upgrade kimi-code")
        print(out2)
        if rc2 != 0:
            print(f"pip 升级失败: {err2}", file=sys.stderr)
            sys.exit(1)

    # 5. 验证
    out, err, rc = run("kimi --version")
    if rc == 0:
        print(f"升级成功，当前版本: {out.strip()}")
    else:
        print("升级后验证失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
