from sqlalchemy import Column, String, Integer, DateTime, Float, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ...core.database import Base

class Keyword(Base):
    """트렌드 키워드 테이블"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), nullable=False, index=True)
    country = Column(String(10), nullable=False, index=True)
    trend_volume = Column(Integer, default=0)
    rank = Column(Integer, default=0)
    
    # 수집 메타데이터
    keyword_collected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 집계 필드 (외래 데이터 카운트)
    instagram_posts = Column(Integer, default=0)
    youtube_videos = Column(Integer, default=0)
    news_count = Column(Integer, default=0)
    score = Column(Float, default=0.0)  # 종합 점수
    
    # 관계 설정 (1:N)
    # 문자열로 클래스명을 참조하므로 순환 참조 문제 없음
    instagram_contents = relationship("InstagramContent", back_populates="keyword_ref", cascade="all, delete-orphan")
    youtube_contents = relationship("YouTubeContent", back_populates="keyword_ref", cascade="all, delete-orphan")
    news_contents = relationship("NewsContent", back_populates="keyword_ref", cascade="all, delete-orphan")
    
    # 복합 인덱스 (국가별 키워드 검색 최적화)
    __table_args__ = (
        Index('ix_keywords_country_collected', 'country', 'keyword_collected_at'),
    )
