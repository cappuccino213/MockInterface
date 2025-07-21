# 使用官方Python基础镜像（slim），减少镜像体积
FROM python:3.13-slim
# 设置作者信息
LABEL authors="zhangyp"

# 开放端口
EXPOSE 8888

# 避免生成.pyc文件
ENV PYTHONDONTWRITEBYTECODE=1

# 关闭输出缓冲，方便日志记录
ENV PYTHONUNBUFFERED=1

# 设置时区
ENV TZ=Asia/Shanghai


# 设置工作目录
WORKDIR /mock_interface

# 复制程序相关文件
COPY requirements.txt /mock_interface/
COPY . /mock_interface

# 更新apt且安装依赖
#RUN apt-get update && apt-get upgrade -y  \
#    && apt-get install -y --no-install-recommends  \
#    fontconfig \
#    libfreetype6 \
#    libjpeg62-turbo \
#    libpng16-16 \
#    libx11-6 \
#    libxext6 \
#    libxdmcp6 \
#    libxrender1 \
#    xfonts-75dpi \
#    xfonts-base

## 安装wkhtmltox
#RUN dpkg -i ./static/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb && apt-get install -f -y


# 使用阿里云镜像加速依赖下载，同时确保安装过程的错误能被捕获
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ && echo "Dependencies installed successfully."

# 指定容器启动时的命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]