from typing import List, Dict, Any
from ...core.database import fetch_one, execute, fetch_all

class NewsRepository:
    def __init__(self):
        pass

    async def save_articles(self, keyword_id: int, country: str, articles: List[Dict[str, Any]]):
        """뉴스 기사 저장 (Upsert)"""
        for article in articles:
            url = article.get('url', '')
            if not url:
                continue

            # 중복 체크
            sql_check = "SELECT id FROM news_contents WHERE url = %s"
            existing = await fetch_one(sql_check, (url,))
            
            if existing:
                # 업데이트 (소속 키워드 갱신)
                sql_update = "UPDATE news_contents SET keyword_id = %s, collected_at = NOW() WHERE id = %s"
                await execute(sql_update, (keyword_id, existing['id']))
            else:
                # 신규
                sql_insert = """
                    INSERT INTO news_contents 
                    (keyword_id, keyword_country, title, source, description, published_at, url, collected_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """
                await execute(sql_insert, (
                    keyword_id,
                    country,
                    article.get('title'),
                    article.get('source'),
                    article.get('description', ''),
                    article.get('published_at'),
                    url
                ))

    async def get_by_keyword(self, keyword_id: int, limit: int = 50) -> List[dict]:
        sql = "SELECT * FROM news_contents WHERE keyword_id = %s LIMIT %s"
        return await fetch_all(sql, (keyword_id, limit))
