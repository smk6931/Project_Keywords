from typing import List, Dict, Any
from loguru import logger
from ...core.database import fetch_one, execute, fetch_all

class YouTubeRepository:
    def __init__(self):
        pass

    async def save_videos(self, keyword_id: int, country: str, videos: List[Dict[str, Any]]) -> Dict[str, int]:
        """유튜브 비디오 리스트 저장 (Upsert)"""
        saved_count = 0
        skipped_count = 0
        
        for video in videos:
            try:
                video_id = video.get("video_id")
                
                # 중복 체크
                sql_check = "SELECT id FROM youtube_contents WHERE video_id = :video_id"
                existing = await fetch_one(sql_check, {"video_id": video_id})
                
                if existing:
                    # 업데이트
                    await execute(
                        """
                        UPDATE youtube_contents 
                        SET keyword_id = :keyword_id, collected_at = NOW(), views = :views, likes = :likes
                        WHERE id = :id
                        """,
                        {
                            "keyword_id": keyword_id,
                            "views": video.get("views", 0),
                            "likes": video.get("likes", 0),
                            "id": existing['id']
                        }
                    )
                    skipped_count += 1
                else:
                    # 신규 저장
                    await execute(
                        """
                        INSERT INTO youtube_contents 
                        (keyword_id, keyword_country, video_id, title, channel, views, likes, published_at, url, collected_at)
                        VALUES (:keyword_id, :country, :video_id, :title, :channel, :views, :likes, :published_at, :url, NOW())
                        """,
                        {
                            "keyword_id": keyword_id,
                            "country": country,
                            "video_id": video_id,
                            "title": video.get("title"),
                            "channel": video.get("channel"),
                            "views": video.get("views", 0),
                            "likes": video.get("likes", 0),
                            "published_at": video.get("published_at"),
                            "url": video.get("url")
                        }
                    )
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"YouTube Repo 저장 실패: {video.get('title')} - {e}")
                continue
        
        return {"saved": saved_count, "skipped": skipped_count}

    async def get_by_keyword(self, keyword_id: int, limit: int = 10) -> List[dict]:
        """키워드별 유튜브 콘텐츠 조회"""
        sql = "SELECT * FROM youtube_contents WHERE keyword_id = :keyword_id LIMIT :limit"
        return await fetch_all(sql, {"keyword_id": keyword_id, "limit": limit})
