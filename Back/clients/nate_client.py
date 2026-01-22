
import requests
from bs4 import BeautifulSoup
from typing import List
from loguru import logger
from ..utils.execution_utils import handle_exception

class NateClient:
    """Nate 실시간 이슈 키워드 수집 클라이언트"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    @handle_exception(error_msg="Nate 트렌드 수집 실패", default=[])
    async def get_realtime_trends(self) -> List[str]:
        """
        Nate 메인 페이지에서 실시간 이슈 키워드 수집
        :return: ['키워드1', '키워드2', ...]
        """
        # Nate는 메인 페이지 혹은 뉴스 페이지에 실시간 이슈를 노출함.
        # 모바일 페이지(m.nate.com)가 구조가 단순하여 크롤링에 유리할 수 있음.
        # PC: www.nate.com -> .isKeyword
        
        url = "https://www.nate.com/"
        logger.info(f"Nate 트렌드 수집 시도: {url}")
        
        response = requests.get(url, headers=self.headers, timeout=5)
        if response.status_code != 200:
            logger.warning(f"Nate 접속 실패: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        keywords = []
        
        # Nate 메인 '실시간 이슈' 영역 (isKeyword 클래스)
        # 5개~10개 정도 롤링됨.
        items = soup.select(".isKeyword a")
        
        for item in items:
            # 텍스트 정제 (순위 숫자나 'new' 뱃지 텍스트 제거 필요할 수 있음)
            # 보통 <span>1</span> 키워드 <span>new</span> 구조임.
            # item.text는 '1 키워드 new' 처럼 나올 수 있음.
            # 순수 키워드만 발라내기 위해 자식 노드 활용하거나 정규식 써야 함.
            # Nate 구조:
            # <a href="...">
            #   <span class="num">1</span>
            #   <span class="txt">손흥민 골</span>
            #   <span class="icon_new">...</span>
            # </a>
            
            txt_span = item.select_one(".txt_rank") # 클래스명이 txt_rank 혹은 txt 일 수 있음. 확인 필요.
            # 방금 check_kr_alts.py 돌렸을 때 단순히 text.strip()으로 가져왔었음.
            # ['단식 장동혁', '이정후 LA', ...] 이렇게 잘 나왔으므로 text 기반으로 추출하되
            # 숫자나 new가 붙어있으면 제거하는 로직이 안전.
            
            raw_text = item.text.strip()
            
            # 간단한 정제: 숫자 패턴 제거? 
            # 하지만 방금 결과가 깨끗했으므로 일단 raw_text 사용.
            # 만약 '1\n키워드\nnew' 식이라면 splitlines()로 처리.
            
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            # 보통 키워드가 가장 긴 줄이거나 특정 위치.
            # 네이트의 경우 HTML 구조상 텍스트가 분리되어 있을 수 있음.
            # 예시 출력: ['단식 장동혁'] -> 깔끔함.
            
            word = lines[0] if lines else raw_text
            
            # 2글자 이상만
            if len(word) >= 2 and word not in keywords:
                keywords.append(word)
                
        if keywords:
            logger.info(f"✅ Nate 트렌드 수집 성공: {len(keywords)}개 - {keywords[:5]}")
            return keywords
            
        logger.warning("Nate 키워드 추출 실패 (Selector 불일치)")
        return []
