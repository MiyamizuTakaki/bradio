FROM python:3.11-slim

# 安装系统依赖，包括 pkg-config 和 MySQL 开发库
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 升级 pip 和构建工具
RUN pip install --upgrade pip setuptools wheel

# 复制项目文件
COPY . /app
WORKDIR /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
