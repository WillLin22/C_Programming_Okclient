#!/usr/bin/env bash
set -e

# ================================
# Build script for okpy-slim
# WillLin, 2025
# ================================

# 1. 清理旧目录
echo "[1/4] 清理 build 目录..."
rm -rf build ok.pyz ok
mkdir -p build

# 2. 安装依赖 + 项目源码到 build/
echo "[2/4] 安装依赖到 build/"
pip install . --target build

# 3. 确保有 __main__.py
# zipapp 必须有 __main__.py 作为入口，这里动态写入一份
echo "[3/4] 生成 __main__.py"
cat > build/__main__.py <<EOF
from client.ok import main

if __name__ == "__main__":
    main()
EOF

# 4. 打包成 zipapp 可执行文件
echo "[4/4] 打包成 ok 可执行文件"
python3 -m zipapp build -o ok -p "/usr/bin/env python3"

chmod +x ok
echo " 打包完成: ./ok"
echo "   运行示例: ./ok --help"