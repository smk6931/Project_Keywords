"""
데이터베이스 설정 (Raw SQL + AsyncConnectionPool)
"""
import os
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# 환경 변수 로드
# 환경 변수 로드
DB_USER = os.getenv("DB_USER", "Project_Keyword")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5440") # 포트 주의! (Docker: 5440)
DB_NAME = os.getenv("DB_NAME", "Project_Keyword")

# Connection String
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 1. SQLAlchemy Engine (Alembic 및 DDL 생성용)
# psycopg(v3) 사용 명시
ALEMBIC_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
engine = create_engine(ALEMBIC_URL, echo=False)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# [중요] Alembic이 모델을 인식할 수 있도록 모델들을 여기서 Import
# 새 모델이 생기면 아래에 추가하세요.
from ..trend.models import *  # noqa: F401, F403

# 2. Async Connection Pool (실제 쿼리 실행용)
pool: AsyncConnectionPool = None

async def init_pool():
    """DB 연결 풀 초기화 (앱 시작 시 호출)"""
    global pool
    try:
        pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            kwargs={"row_factory": dict_row}, 
            min_size=1,
            max_size=50,
            open=False, # 명시적으로 open 호출 위해
            timeout=5.0 # 5초 타임아웃
        )
        await pool.open()
        
        # 연결 테스트 (Ping)
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                
        print(f"🔥 DB pool initialized (Raw SQL) - Connected to {DB_HOST}:{DB_PORT}/{DB_NAME}")
        
    except Exception as e:
        safe_url = DATABASE_URL.replace(DB_PASSWORD, "****") if DB_PASSWORD else DATABASE_URL
        print(f"❌ DB 연결 실패: {e}")
        print(f"   URL: {safe_url}")
        # 연결 실패해도 앱이 죽지 않도록 예외를 다시 던지지 않음 (필요 시 수정)
        raise e

async def close_pool():
    """DB 연결 풀 종료 (앱 종료 시 호출)"""
    global pool
    if pool:
        await pool.close()
        print("🧹 DB pool closed")

def get_pool() -> AsyncConnectionPool:
    if pool is None:
        raise RuntimeError("DB pool is not initialized")
    return pool

# ===== Raw SQL 헬퍼 함수 =====

async def fetch_one(sql: str, params=()) -> dict | None:
    """단일 행 조회"""
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()

async def fetch_all(sql: str, params=()) -> list[dict]:
    """다중 행 조회"""
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchall()

async def execute(sql: str, params=()):
    """단순 실행 (INSERT, UPDATE, DELETE)"""
    async with pool.connection() as conn:
        try:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
            await conn.commit()
        except Exception as e:
            print(f"❌ execute 실패: {e}")
            await conn.rollback()
            raise e

async def execute_return(sql: str, params=()) -> dict | None:
    """실행 후 결과 반환 (RETURNING 절 사용 시)"""
    async with pool.connection() as conn:
        try:
            async with conn.cursor() as cur:
                await cur.execute(sql, params)
                row = await cur.fetchone()
            await conn.commit()
            return row
        except Exception as e:
            print(f"❌ execute_return 실패: {e}")
            await conn.rollback()
            raise e

# (구) 의존성 함수 - 이제 사용하지 않음 (Router 수정 시 제거 예정)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
