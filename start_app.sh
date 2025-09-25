#!/bin/bash

# 专家评分系统启动脚本

echo "启动专家评分系统..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 启动应用
echo "启动Flask应用..."
echo "访问地址: http://localhost:5001"
echo "管理员页面: http://localhost:5001/admin/ratings"
echo ""
echo "按 Ctrl+C 停止服务器"

python app.py
