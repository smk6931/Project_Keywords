from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ...core.database import Base

class YouTubeContent(Base):
    """유튜브 콘텐츠 테이블"""
    __tablename__ = "youtube_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), index=True)
    
    # 유튜브 고유 정보
    video_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(300))
    channel = Column(String(200))
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    published_at = Column(String(50))
    url = Column(String(300))
    
    # 수집 메타
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    keyword_country = Column(String(10))
    
    # 관계
    keyword_ref = relationship("Keyword", back_populates="youtube_contents")
