# 使用 Python 3.11 作为基础镜像
FROM python:3.11-slim

# 安装 fontconfig 用于字体管理
RUN apt-get update && apt-get install -y fontconfig && apt-get clean

# 将字体文件从项目复制到容器中的字体目录
COPY fonts/SimHei.ttf /usr/share/fonts/truetype/simhei/SimHei.ttf

# 刷新字体缓存
RUN fc-cache -fv

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
