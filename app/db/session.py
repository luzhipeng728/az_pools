from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
  
DB_USER = os.getenv("POSTGRES_USER", "youruser") # 默认值是你原始的用户名称
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "yourpassword") # 默认值是你原始的密码
DB_HOST = os.getenv("DB_HOST", "localhost") # 默认值是localhost，对于Docker应该设置为db
DB_NAME = os.getenv("POSTGRES_DB", "yourdatabase") # 默认值是你原始的数据库名称

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)