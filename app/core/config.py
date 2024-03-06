import os
import redis

# 从环境变量获取Redis的URL
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.Redis.from_url(redis_url)