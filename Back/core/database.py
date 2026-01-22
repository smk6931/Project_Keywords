"""
데이터베이스 설정 (SQLAlchemy Async Engine + asyncpg)
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# 1. 비동기 엔진 생성
# config.py의 설정을 사용 (postgresql+asyncpg://...)
# 덮어쓰기: config.py의 기본값은 'postgresql+asyncpg://' 가 아니라면 수정 필요
# 사용자님의 docker-compose 환경에 맞게 자동 구성
# config.py의 DATABASE_URL이 ORM용(psycopg)일 수 있으므로 여기서 재구성하거나 config를 믿음.
# 안전하게 여기서 조합합니다.

# DATABASE_URL 재조립 (asyncpg 드라이버 강제)
ASYNC_DB_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_async_engine(
    ASYNC_DB_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.DEBUG  # 디버그 모드일 때 쿼리 로그 출력
)

# 2. Base 선언 (Alembic용)
Base = declarative_base()

# 중요: Alembic 모델 인식용 import
from ..trend.models import *  # noqa: F401

# 3. Raw SQL 헬퍼 함수 (SQLAlchemy Core 사용)

async def fetch_one(query: str, params: dict = None) -> dict | None:
    """SELECT 단건 조회 (결과를 dict로 반환)"""
    async with engine.connect() as conn:
        # text()로 감싸서 실행
        result = await conn.execute(text(query), params or {})
        row = result.mappings().first()
        return dict(row) if row else None

async def fetch_all(query: str, params: dict = None) -> list[dict]:
    """SELECT 다건 조회"""
    async with engine.connect() as conn:
        result = await conn.execute(text(query), params or {})
        rows = result.mappings().all()
        return [dict(row) for row in rows]

async def execute(query: str, params: dict = None):
    """INSERT, UPDATE, DELETE (자동 커밋)"""
    async with engine.begin() as conn:
         await conn.execute(text(query), params or {})

async def execute_return(query: str, params: dict = None) -> dict | None:
    """INSERT/UPDATE 후 결과 반환 (RETURNING)"""
    async with engine.begin() as conn:
        result = await conn.execute(text(query), params or {})
        row = result.mappings().first()
        return dict(row) if row else None

# 4. Pool Lifecycle (main.py에서 사용)
async def init_pool():
    # SQLAlchemy Engine은 Lazy Connect라 명시적 init 불필요하지만
    # 연결 테스트를 위해 핑을 한번 날려봄
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print(f"🔥 Async DB Engine initialized - Connected to {settings.DB_HOST}:{settings.DB_PORT}")
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        # raise e  # 필요 시 주석 해제

async def close_pool():
    await engine.dispose()
    print("🧹 Async DB Engine disposed")
