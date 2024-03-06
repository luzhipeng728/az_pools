# 选择基础镜像
FROM python:3.8
# 安装 PostgreSQL 客户端、supervisor
RUN apt-get update && apt-get install -y postgresql-client supervisor
# 设置工作目录
WORKDIR /app
# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 复制并设置 scripts 目录中的脚本权限
COPY ./scripts /scripts
RUN chmod +x /scripts/docker-entrypoint.sh
# 设置 supervisor 配置文件
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# 给定时任务脚本执行权限（根据需要调整脚本位置和权限设置）
COPY run_every_10s.sh /scripts
RUN chmod +x /scripts/run_every_10s.sh
# 设置启动命令为 docker-entrypoint.sh，内部应该启动 supervisord
ENTRYPOINT ["/scripts/docker-entrypoint.sh"]