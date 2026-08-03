"""Thiết lập SQLAlchemy."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db():
    """Dependency của FastAPI - mở/đóng phiên CSDL cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def tu_bo_sung_cot():
    """Tự thêm cột còn thiếu vào CSDL cũ (SQLite) để không mất dữ liệu khi nâng cấp.

    So sánh cột khai báo trong model với cột thực có; cột nào thiếu thì ALTER TABLE
    ADD COLUMN. Chỉ áp dụng cho SQLite (bản chạy nội bộ mặc định).
    """
    from sqlalchemy import inspect, text

    if not DATABASE_URL.startswith("sqlite"):
        return
    insp = inspect(engine)
    ten_bang = set(insp.get_table_names())
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in ten_bang:
                continue
            co_san = {c["name"] for c in insp.get_columns(table.name)}
            for col in table.columns:
                if col.name in co_san:
                    continue
                kieu = col.type.compile(dialect=engine.dialect)
                conn.execute(text(
                    f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {kieu}'))
