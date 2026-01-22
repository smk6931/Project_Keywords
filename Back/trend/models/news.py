from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ...core.database import Base

class NewsContent(Base):
    """뉴스 콘텐츠 테이블"""
    __tablename__ = "news_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), index=True)
    
    # 뉴스 고유 정보
    title = Column(String(300))
    source = Column(String(100))
    description = Column(Text)
    published_at = Column(String(50))
    url = Column(Text, unique=True)
    
    # 수집 메타
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    keyword_country = Column(String(10))
    
    # 관계
    keyword_ref = relationship("Keyword", back_populates="news_contents")
