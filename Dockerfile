# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 安装 SimHei 字体和其他所需的依赖
RUN apt-get update && apt-get install -y \
    fontconfig \
    && mkdir -p /usr/share/fonts/chinese \
    && cd /usr/share/fonts/chinese \
    && apt-get install -y wget \
    && wget https://github.com/adamzy/simhei/raw/master/SimHei.ttf \
    && fc-cache -fv

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器中的工作目录
COPY . /app

# 复制 requirements.txt 文件
COPY requirements.txt /app/requirements.txt

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露 Flask 默认的运行端口
EXPOSE 8080

# 启动 Flask 应用
CMD ["python", "main.py"]
