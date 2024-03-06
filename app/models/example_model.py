from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from ..db.base_class import Base



class AZKey(Base):
    __tablename__ = "az_keys"

    id = Column(Integer, primary_key=True, index=True)
    resourcename = Column(String, index=True)  # 注意这里的大小写
    key = Column(String)
    status = Column(String, default="normal")
    # addtime = Column(TIMESTAMP, server_default=func.now())
    is_in_use = Column(Boolean, default=False)
    
    # 在AZKey模型内
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}