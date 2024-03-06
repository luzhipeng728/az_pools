#!/bin/bash
set -e

echo "Connecting to DB with user: $POSTGRES_USER, Db: $POSTGRES_DB, Host: $DB_HOST"

# 等待Postgres服务启动
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# 在执行SQL脚本之前确保POSTGRES_PASSWORD环境变量已导出
export PGPASSWORD=$POSTGRES_PASSWORD

# 执行SQL脚本初始化数据库
psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -a -f /scripts/init_db.sql

# 清除环境变量，避免泄漏敏感信息
unset PGPASSWORD

# 执行docker命令
exec "$@"

# 最后启动 supervisor，管理其他进程。
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf