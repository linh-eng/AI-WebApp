"""Cấu hình ứng dụng - đọc từ biến môi trường, có giá trị mặc định để chạy ngay."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# CSDL: mặc định SQLite trong thư mục data/. Đổi sang PostgreSQL bằng biến DATABASE_URL.
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'thng.db'}")

# Khoá ký cookie phiên đăng nhập. BẮT BUỘC đổi khi chạy thật (biến SECRET_KEY).
SECRET_KEY = os.getenv("SECRET_KEY", "thay-doi-khoa-nay-khi-chay-that-1234567890")

# File Excel mẫu dùng làm template khi xuất báo cáo.
TEMPLATE_XLSX = Path(
    os.getenv(
        "TEMPLATE_XLSX",
        BASE_DIR / "docs" / "templates" / "Mau_bao_cao_kinh_doanh_THNG.xlsx",
    )
)

# Tài khoản admin khởi tạo lần đầu.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Token cho REST API (để phần mềm khác đọc số liệu). Đổi khi chạy thật.
API_TOKEN = os.getenv("API_TOKEN", "thng-api-token-doi-di")

# Tự động chốt báo cáo cuối tháng (True/False) và khoảng kiểm tra (giây).
TU_DONG_CHOT = os.getenv("TU_DONG_CHOT", "true").lower() == "true"
