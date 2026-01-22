from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ...core.database import Base

class InstagramContent(Base):
    """인스타그램 콘텐츠 테이블"""
    __tablename__ = "instagram_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), index=True)
    
    # 인스타그램 고유 정보
    post_id = Column(String(100), unique=True, nullable=False)
    username = Column(String(100))
    caption = Column(Text)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    timestamp = Column(String(50))  # ISO 형식 문자열
    url = Column(String(300))
    
    # 수집 메타
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    keyword_country = Column(String(10))
    
    # 관계
    keyword_ref = relationship("Keyword", back_populates="instagram_contents")
