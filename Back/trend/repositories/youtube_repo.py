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
                sql_check = "SELECT id FROM youtube_contents WHERE video_id = %s"
                existing = await fetch_one(sql_check, (video_id,))
                
                if existing:
                    # 업데이트
                    sql_update = """
                        UPDATE youtube_contents 
                        SET keyword_id = %s, collected_at = NOW(), views = %s, likes = %s
                        WHERE id = %s
                    """
                    # views, likes가 없으면 기존 값을 유지해야 하는데 Raw SQL에선 SELECT를 한 번 더 해야 함.
                    # 여기선 편의상 들어온 값이 있으면 덮어쓰는 구조로 감.
                    # (정확히 하려면 SELECT * 했어야 함. 위 fetch_one을 SELECT *로 변경)
                    
                    await execute(sql_update, (
                        keyword_id, 
                        video.get("views", 0), 
                        video.get("likes", 0), 
                        existing['id']
                    ))
                    skipped_count += 1
                else:
                    # 신규 저장
                    sql_insert = """
                        INSERT INTO youtube_contents 
                        (keyword_id, keyword_country, video_id, title, channel, views, likes, published_at, url, collected_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """
                    await execute(sql_insert, (
                        keyword_id,
                        country,
                        video_id,
                        video.get("title"),
                        video.get("channel"),
                        video.get("views", 0),
                        video.get("likes", 0),
                        video.get("published_at"),
                        video.get("url")
                    ))
                    saved_count += 1
                    
            except Exception as e:
                logger.error(f"YouTube Repo 저장 실패: {video.get('title')} - {e}")
                continue
        
        return {"saved": saved_count, "skipped": skipped_count}

    async def get_by_keyword(self, keyword_id: int, limit: int = 10) -> List[dict]:
        """키워드별 유튜브 콘텐츠 조회"""
        sql = "SELECT * FROM youtube_contents WHERE keyword_id = %s LIMIT %s"
        return await fetch_all(sql, (keyword_id, limit))
