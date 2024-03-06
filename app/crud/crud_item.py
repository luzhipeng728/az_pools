from sqlalchemy.orm import Session
from app.models.example_model import AZKey
import json
from datetime import datetime
from app.core.config import redis_client
from fastapi import Query
from functools import wraps

# 定义一个装饰器，用于数据变更后自动重建缓存
# def auto_rebuild_caches(func):
#     @wraps(func)
#     async def wrapper(db: Session, *args, **kwargs):
#         result = await func(db, *args, **kwargs)
#         await rebuild_caches(db)  # 调用重建缓存的方法
#         return result
#     return wrapper

# 序列化方法，用于处理 datetime
def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

# 重建缓存
async def rebuild_caches(db: Session):
    permanent_in_use_count_key = "permanent_in_use_count"
    default_in_use_count = 6
    # 尝试获取 permanent_in_use_count_key 的值，如果不存在，使用默认值
    permanent_in_use_count = redis_client.get(permanent_in_use_count_key)
    if permanent_in_use_count is None or default_in_use_count <= 0:
        # 如果没有设置过永久 in_use_count，使用默认值并在 Redis 中设置这个默认值
        permanent_in_use_count = default_in_use_count
        redis_client.set(permanent_in_use_count_key, permanent_in_use_count)
    else:
        permanent_in_use_count = int(permanent_in_use_count)
    # 重建 all_keys 缓存
    objs = db.query(AZKey).order_by(AZKey.id.asc()).all()
    all_keys = [{c.name: getattr(obj, c.name) for c in AZKey.__table__.columns} for obj in objs]
    # redis_client.set("all_keys", json.dumps(all_keys, default=datetime_serializer))

    # 筛选正常状态的 AZKey，并根据 permanent_in_use_count 的值限制结果数量, 同时按 id 升序排序
    normal_objs = db.query(AZKey).filter(AZKey.status == 'normal').order_by(AZKey.id.asc()).limit(permanent_in_use_count).all()
    normal_in_use_count_keys = [{c.name: getattr(obj, c.name) for c in AZKey.__table__.columns} for obj in normal_objs]
    # redis_client.set("normal_in_use_count_keys", json.dumps(normal_in_use_count_keys, default=datetime_serializer))
    
    return all_keys, normal_in_use_count_keys
    

# 添加 AZKey
# 示例逻辑
async def add_az_key(db: Session, az_key_data: dict):
    # 检查是否存在相同的key
    existing_key = db.query(AZKey).filter(AZKey.key == az_key_data["key"]).first()
    if existing_key:
        # 返回一个错误信息，因为key值已经存在
        return {"status": "error", "message": "The provided 'key' value already exists."}
    # 如果key值是唯一的，则继续执行插入操作

    try:
        az_key = AZKey(**az_key_data)
        db.add(az_key)
        db.commit()
        db.refresh(az_key)
        await get_normal_az_keys(db, -1, force_update=True)
        return {"status": "success", "message": "AZKey added successfully.", "az_key": az_key}
    except Exception as e:
        db.rollback()  # 显式回滚，以应对其他可能的异常
        return {"status": "error", "message": "Error adding AZKey."}

# @auto_rebuild_caches
async def update_az_key(db: Session, az_key_id: int, new_data: dict):
    obj = db.query(AZKey).filter(AZKey.id == az_key_id).first()
    if obj:
        try:
            for key, value in new_data.items():
                setattr(obj, key, value)
            db.commit()
            return {"status": "success", "message": "AZKey updated successfully."}
        except Exception as e:
            print(f"Error updating AZKey: {e}")
            return {"status": "error", "message": "Error updating AZKey."}
    else:
        return {"status": "error", "message": "AZKey not found."}

# @auto_rebuild_caches
async def delete_az_key(db: Session, az_key_id: int):
    obj = db.query(AZKey).filter(AZKey.id == az_key_id).first()
    if obj:
        try:
            db.delete(obj)
            db.commit()
            return {"status": "success", "message": "AZKey deleted successfully."}
        except Exception as e:
            print(f"Error deleting AZKey: {e}")
            return {"status": "error", "message": "Error deleting AZKey."}
    else:
        return {"status": "error", "message": "AZKey not found."}
        
# 获取所有的 AZKey 对象
async def get_all_az_keys(db: Session):
    cache_key = "all_keys"
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    else:
        # 从数据库获取，并更新缓存
        objs = db.query(AZKey).order_by(AZKey.id.asc()).all()
        result = [{c.name: getattr(obj, c.name) for c in AZKey.__table__.columns} for obj in objs]
        redis_client.set(cache_key, json.dumps(result, default=datetime_serializer))
        return result


from sqlalchemy.sql import text

async def get_normal_az_keys(db: Session, in_use_count: int = -1, force_update: bool=False):
    # default_cache_key = "normal_in_use_count_keys"
    permanent_in_use_count_key = "permanent_in_use_count"
    # cached_result = None
    if in_use_count is None:
        in_use_count = -1

    permanent_in_use_count = redis_client.get(permanent_in_use_count_key)
    if permanent_in_use_count:
        permanent_in_use_count = int(permanent_in_use_count)
    else:
        permanent_in_use_count = 6
    if force_update:
        if in_use_count <= 0:
            in_use_count = permanent_in_use_count
        permanent_in_use_count = in_use_count
        redis_client.set(permanent_in_use_count_key, permanent_in_use_count)
        update_query_in_use = text("""
            UPDATE az_keys
            SET is_in_use = TRUE 
            WHERE id IN (
                SELECT id
                FROM az_keys
                WHERE status = 'normal'
                ORDER BY id
                LIMIT :limit
            ) AND status = 'normal'
        """)
        db.execute(update_query_in_use, params={'limit': in_use_count})
        # Then, update the rest of the az_keys to FALSE
        update_query_not_in_use = text("""
            UPDATE az_keys
            SET is_in_use = FALSE
            WHERE id NOT IN (
                SELECT id
                FROM az_keys
                WHERE status = 'normal'
                ORDER BY id
                LIMIT :limit
            )
        """)
        db.execute(update_query_not_in_use, params={'limit': in_use_count})
        db.commit()
    _, normal_keys = await rebuild_caches(db)  # Ensure this function is correctly defined and implemented
    return normal_keys
              
        

async def get_az_key_by_id(db: Session, az_key_id: int):
    # 直接从数据库查询
    az_key = db.query(AZKey).filter(AZKey.id == az_key_id).first()
    return az_key

async def update_az_key_crud(db: Session, az_key_id: int, new_data: dict):
    obj = db.query(AZKey).filter(AZKey.id == az_key_id).first()
    if not obj:
        return None  # Indicate that the object was not found
    
    for key, value in new_data.items():
        setattr(obj, key, value)
    
    db.commit()
    await get_normal_az_keys(db, in_use_count=None, force_update=True)
    return obj