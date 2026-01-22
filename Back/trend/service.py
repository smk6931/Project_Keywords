"""
트렌드 수집 비즈니스 로직
"""
from loguru import logger
from datetime import datetime

from .schemas import TrendCollectionResponse

# API Clients
from ..clients.youtube_client import YouTubeClient
from ..clients.rss_client import RSSClient
from ..clients.scraper_client import ScraperClient

# Repositories
from .repositories.keyword_repo import KeywordRepository
from .repositories.youtube_repo import YouTubeRepository
from .repositories.news_repo import NewsRepository

class TrendService:
    """트렌드 수집 및 분석 서비스 (Repository Pattern 적용)"""
    
    def __init__(self):
        # Clients
        self.youtube_client = YouTubeClient()
        self.rss_client = RSSClient()
        self.scraper_client = ScraperClient()
        
        # Repositories (Raw SQL 방식이므로 세션 불필요)
        self.keyword_repo = KeywordRepository()
        self.youtube_repo = YouTubeRepository()
        self.news_repo = NewsRepository()

    async def collect_trending_contents(self, country: str) -> TrendCollectionResponse:
        """
        실시간 인기 콘텐츠 수집 로직
        """
        logger.info(f"🔥 실시간 인기 콘텐츠 수집 시작: {country}")
        
        # 1. 키워드 ID 확보
        keyword_obj = await self.keyword_repo.get_or_create_daily_keyword(country)
        # Raw SQL 결과는 Dict이므로 ['id'] 접근
        keyword_id = keyword_obj['id']
        
        # 2. YouTube 수집
        youtube_count = 0
        videos = await self.youtube_client.get_trending_videos(country, max_results=20)
        
        # [Plan B] 한국인데 0개면 실검 기반 검색
        if not videos and country == 'KR':
            logger.warning("⚠️ YouTube Trending 0개 -> 실시간 검색어로 대체 수집 시도")
            signal_keywords = await self.scraper_client.crawl_signal_bz()
            if signal_keywords:
                top_keyword = signal_keywords[0]['keyword']
                logger.info(f"🔎 대체 검색어: {top_keyword}")
                videos = await self.youtube_client.search_videos(top_keyword, max_results=10)

        # 3. YouTube 저장
        if videos:
            result = await self.youtube_repo.save_videos(keyword_id, country, videos)
            youtube_count = result['saved'] + result['skipped']
            logger.info(f"✅ YouTube 처리: 신규 {result['saved']}, 중복 {result['skipped']}")
        
        # 4. News/Signal 수집
        news_count = 0
        articles = await self.rss_client.fetch_google_news(country)
        
        if country == 'KR':
            signal_keywords = await self.scraper_client.crawl_signal_bz()
            if signal_keywords:
                logger.info(f"✅ Signal.bz 추가: {len(signal_keywords)}개")
                for item in reversed(signal_keywords): # 역순 insert로 순서 유지
                    articles.insert(0, {
                        'keyword': f"🔥 {item['keyword']}",
                        'url': '',
                        'published_at': datetime.now().isoformat()
                    })

        if articles:
            # RSS 포맷 -> DB 모델 스키마 매핑
            news_list = []
            for article in articles:
                # URL 생성 로직
                final_url = article.get('url')
                if not final_url and '🔥' in article['keyword']:
                     clean_keyword = article['keyword'].replace('🔥 ', '')
                     final_url = f"https://www.google.com/search?q={clean_keyword}"

                news_list.append({
                    'title': article['keyword'],
                    'source': 'Google News' if 'keyword' in article and '🔥' not in article['keyword'] else '실시간 검색어',
                    'description': '',
                    'url': final_url or '',
                    'published_at': article.get('published_at') or datetime.now().isoformat()
                })
            
            # 5. News 저장
            await self.news_repo.save_articles(keyword_id, country, news_list)
            news_count = len(news_list)
            logger.info(f"✅ News 저장: {news_count}개")
        
        # 6. 통계 업데이트 (Commit은 Repo 내부 execute에서 수행됨)
        await self.keyword_repo.update_statistics(keyword_id)
        
        total = youtube_count + news_count
        logger.info(f"🎉 수집 완료: 총 {total}건")
        
        return TrendCollectionResponse(
            success=True,
            message=f"콘텐츠 {total}개 수집 완료",
            keywords_count=total
        )
