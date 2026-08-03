"""Cấu hình ứng dụng - đọc từ biến môi trường, có giá trị mặc định để chạy ngay."""
import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# CSDL: mặc định SQLite trong thư mục data/. Đổi sang PostgreSQL bằng biến DATABASE_URL.
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'thng.db'}")


def _secret_key() -> str:
    """Khoá ký cookie đăng nhập. Ưu tiên biến SECRET_KEY; nếu không có thì tự sinh
    một khoá ngẫu nhiên và lưu lại (mỗi lần cài đặt có khoá riêng, ổn định)."""
    env = os.getenv("SECRET_KEY")
    if env:
        return env
    f = DATA_DIR / "secret.key"
    if f.exists():
        return f.read_text().strip()
    val = secrets.token_hex(32)
    f.write_text(val)
    return val


SECRET_KEY = _secret_key()

# File Excel mẫu dùng làm template khi xuất báo cáo.
TEMPLATE_XLSX = Path(
    os.getenv(
        "TEMPLATE_XLSX",
        BASE_DIR / "docs" / "templates" / "BaoCaoMuaHang_DuAn_THNG.xlsx",
    )
)

# Ngưỡng tỷ lệ hàng lỗi cho phép (khớp ô vàng "Tổng quan"!C8 của file mẫu).
NGUONG_HANG_LOI = float(os.getenv("NGUONG_HANG_LOI", "0.02"))

# Tài khoản admin khởi tạo lần đầu.
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Token cho REST API (để phần mềm khác đọc số liệu). Đổi khi chạy thật.
API_TOKEN = os.getenv("API_TOKEN", "thng-api-token-doi-di")

# Tự động chốt báo cáo cuối tháng (True/False) và khoảng kiểm tra (giây).
TU_DONG_CHOT = os.getenv("TU_DONG_CHOT", "true").lower() == "true"

# Thông tin công ty (hiển thị trên PDF báo giá/hợp đồng).
COMPANY_NAME = os.getenv("COMPANY_NAME", "CÔNG TY THNG")
COMPANY_INFO = os.getenv("COMPANY_INFO", "Địa chỉ: ... · ĐT: ... · MST: ...")
