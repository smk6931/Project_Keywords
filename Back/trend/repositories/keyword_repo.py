from datetime import datetime
from ...core.database import fetch_one, execute_return, execute

class KeywordRepository:
    def __init__(self):
        pass # Raw SQL 방식은 db 세션을 멤버로 가질 필요 없음 (Pool 사용)

    async def get_or_create_daily_keyword(self, country: str) -> dict:
        """오늘 날짜의 국가별 트렌드 키워드 객체 조회 또는 생성"""
        today = datetime.now().strftime("%Y%m%d")
        dummy_keyword = f"Trending_{country}_{today}"
        
        # 조회
        sql_select = """
            SELECT * FROM keywords 
            WHERE keyword = %s 
            ORDER BY id DESC LIMIT 1
        """
        keyword_obj = await fetch_one(sql_select, (dummy_keyword,))
        
        # 없으면 생성
        if not keyword_obj:
            sql_insert = """
                INSERT INTO keywords (keyword, country, trend_volume, rank, keyword_collected_at)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING *
            """
            keyword_obj = await execute_return(sql_insert, (dummy_keyword, country, 0, 0))
            
        return keyword_obj

    async def update_statistics(self, keyword_id: int):
        """Youtube/News 카운트 집계 및 점수 갱신"""
        # 유튜브 카운트
        sql_count_yt = "SELECT COUNT(*) as count FROM youtube_contents WHERE keyword_id = %s"
        res_yt = await fetch_one(sql_count_yt, (keyword_id,))
        youtube_count = res_yt['count'] if res_yt else 0
        
        # 뉴스 카운트
        sql_count_news = "SELECT COUNT(*) as count FROM news_contents WHERE keyword_id = %s"
        res_news = await fetch_one(sql_count_news, (keyword_id,))
        news_count = res_news['count'] if res_news else 0
        
        score = (youtube_count * 1.5) + (news_count * 1)
        
        # 업데이트
        sql_update = """
            UPDATE keywords 
            SET youtube_videos = %s, news_count = %s, score = %s
            WHERE id = %s
        """
        await execute(sql_update, (youtube_count, news_count, score, keyword_id))
