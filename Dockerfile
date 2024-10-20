# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器中的工作目录
COPY . /app

# 复制 requirements.txt 文件
COPY requirements.txt /app/requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 默认的运行端口
EXPOSE 8080

# 设置 Flask 环境变量
ENV FLASK_APP=main.py

# 启动 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
