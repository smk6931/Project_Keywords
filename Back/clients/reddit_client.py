
import requests
from typing import List
from loguru import logger
from ..utils.execution_utils import handle_exception

class RedditClient:
    """Reddit Popular 트렌드 수집 클라이언트"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    @handle_exception(error_msg="Reddit 트렌드 수집 실패", default=[])
    async def get_global_trends(self) -> List[str]:
        """
        Reddit r/popular의 상위 토픽 제목을 키워드로 변환
        :return: ['Topic 1', 'Topic 2', ...]
        """
        # API 없이 JSON 엔드포인트 사용
        url = "https://www.reddit.com/r/popular/top.json?limit=25&t=day"
        logger.info(f"Reddit 트렌드 수집 시도: {url}")
        
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.status_code != 200:
            logger.warning(f"Reddit 접속 실패: {response.status_code}")
            return []
            
        data = response.json()
        children = data.get('data', {}).get('children', [])
        
        keywords = []
        for item in children:
            title = item.get('data', {}).get('title', '')
            # 제목이 너무 길면 키워드로 쓰기 부적절할 수 있음.
            # 하지만 Search Query로 쓰기엔 괜찮음.
            # 너무 긴 문장은 좀 자르거나, 그대로 사용.
            if title and len(title) < 100:
                keywords.append(title)
                
        if keywords:
            logger.info(f"✅ Reddit 트렌드 수집 성공: {len(keywords)}개")
            return keywords
            
        return []
