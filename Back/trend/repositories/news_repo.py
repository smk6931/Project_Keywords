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
            existing = await fetch_one(
                "SELECT id FROM news_contents WHERE url = :url",
                {"url": url}
            )
            
            if existing:
                # 업데이트 (소속 키워드 갱신)
                await execute(
                    "UPDATE news_contents SET keyword_id = :keyword_id, collected_at = NOW() WHERE id = :id",
                    {"keyword_id": keyword_id, "id": existing['id']}
                )
            else:
                # 신규
                await execute(
                    """
                    INSERT INTO news_contents 
                    (keyword_id, keyword_country, title, source, description, published_at, url, collected_at)
                    VALUES (:keyword_id, :country, :title, :source, :description, :published_at, :url, NOW())
                    """,
                    {
                        "keyword_id": keyword_id,
                        "country": country,
                        "title": article.get('title'),
                        "source": article.get('source'),
                        "description": article.get('description', ''),
                        "published_at": article.get('published_at'),
                        "url": url
                    }
                )

    async def get_by_keyword(self, keyword_id: int, limit: int = 50) -> List[dict]:
        sql = "SELECT * FROM news_contents WHERE keyword_id = :keyword_id LIMIT :limit"
        return await fetch_all(sql, {"keyword_id": keyword_id, "limit": limit})
