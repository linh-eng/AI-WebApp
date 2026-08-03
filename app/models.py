"""Mô hình dữ liệu - khớp với các sheet NHẬP TAY của file mẫu Báo cáo Mua hàng THNG.

Quy trình:
  1) Check giá:  Dự án -> Check giá (yêu cầu) -> Báo giá (so sánh NCC) -> chọn NCC
  2) PR - PO:    PR (đề nghị mua) -> PO (đơn hàng/hợp đồng) -> tiến độ giao & chất lượng
  3) Thanh toán: Thanh toán -> Công nợ phải trả (tính động)

Chỉ lưu dữ liệu NHẬP TAY; các giá trị công thức (tên dự án, giá trị, tiết kiệm,
công nợ, tuổi nợ...) được tính động ở tầng calculations.py và do file mẫu tự
tính lại khi mở bằng Excel.
"""
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class NguoiDung(Base):
    """Tài khoản người dùng nội bộ."""
    __tablename__ = "nguoi_dung"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    mat_khau_hash: Mapped[str] = mapped_column(String(255))
    ho_ten: Mapped[str] = mapped_column(String(120), default="")
    # Vai trò: nhan_vien | truong_phong | admin
    vai_tro: Mapped[str] = mapped_column(String(20), default="nhan_vien")


class DuAn(Base):
    """Sheet 'Dự án' - danh mục dự án (toàn bộ nhập tay)."""
    __tablename__ = "du_an"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_du_an: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ten: Mapped[str] = mapped_column(String(250), default="")
    khach_hang: Mapped[str] = mapped_column(String(200), default="")
    pm: Mapped[str] = mapped_column(String(120), default="")
    ngay_bat_dau: Mapped[date | None] = mapped_column(Date, nullable=True)
    ngay_ket_thuc: Mapped[date | None] = mapped_column(Date, nullable=True)
    ngan_sach: Mapped[float] = mapped_column(Float, default=0)
    trang_thai: Mapped[str] = mapped_column(String(30), default="Đang thực hiện")
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class NhaCungCap(Base):
    """Sheet 'Nhà cung cấp' - toàn bộ nhập tay."""
    __tablename__ = "nha_cung_cap"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_ncc: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ten: Mapped[str] = mapped_column(String(200), default="")
    nguoi_lien_he: Mapped[str] = mapped_column(String(120), default="")
    dien_thoai: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(120), default="")
    dia_chi: Mapped[str] = mapped_column(String(250), default="")
    dieu_khoan_tt: Mapped[int] = mapped_column(Integer, default=0)  # số ngày
    danh_gia: Mapped[str] = mapped_column(String(10), default="")   # A/B/C
    nhom_hang: Mapped[str] = mapped_column(String(200), default="")
    ma_so_thue: Mapped[str] = mapped_column(String(30), default="")
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class CheckGia(Base):
    """Sheet 'Check giá' - yêu cầu tiếp nhận & xử lý giá (quy trình 1)."""
    __tablename__ = "check_gia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_yc: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ngay_nhan: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_du_an: Mapped[str] = mapped_column(String(30), default="")
    nguoi_yc: Mapped[str] = mapped_column(String(150), default="")
    hang_muc: Mapped[str] = mapped_column(String(300), default="")
    dvt: Mapped[str] = mapped_column(String(30), default="")
    so_luong: Mapped[float] = mapped_column(Float, default=0)
    don_gia_du_toan: Mapped[float] = mapped_column(Float, default=0)
    han_tra_gia: Mapped[date | None] = mapped_column(Date, nullable=True)
    ngay_tra_gia: Mapped[date | None] = mapped_column(Date, nullable=True)
    trang_thai: Mapped[str] = mapped_column(String(30), default="")
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class BaoGia(Base):
    """Sheet 'Báo giá' - mỗi dòng = 1 báo giá của 1 NCC cho 1 YC (quy trình 1)."""
    __tablename__ = "bao_gia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_bao_gia: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ngay: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_yc: Mapped[str] = mapped_column(String(30), default="")
    ma_ncc: Mapped[str] = mapped_column(String(30), default="")
    don_gia: Mapped[float] = mapped_column(Float, default=0)
    thoi_gian_giao: Mapped[float] = mapped_column(Float, default=0)  # số ngày
    hieu_luc: Mapped[date | None] = mapped_column(Date, nullable=True)
    duoc_chon: Mapped[str] = mapped_column(String(5), default="")  # "x" nếu được chọn
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class PR(Base):
    """Sheet 'PR' - đề nghị mua hàng (quy trình 2)."""
    __tablename__ = "pr"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_pr: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ngay: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_yc: Mapped[str] = mapped_column(String(30), default="")
    so_luong: Mapped[float] = mapped_column(Float, default=0)
    don_gia_du_toan: Mapped[float] = mapped_column(Float, default=0)
    ngay_can_hang: Mapped[date | None] = mapped_column(Date, nullable=True)
    trang_thai_duyet: Mapped[str] = mapped_column(String(30), default="")
    nguoi_duyet: Mapped[str] = mapped_column(String(120), default="")
    ngay_duyet: Mapped[date | None] = mapped_column(Date, nullable=True)
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class PO(Base):
    """Sheet 'PO' - đơn mua hàng / hợp đồng + tiến độ giao & chất lượng (quy trình 2)."""
    __tablename__ = "po"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_po: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ngay: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_pr: Mapped[str] = mapped_column(String(30), default="")
    ma_ncc: Mapped[str] = mapped_column(String(30), default="")
    so_luong_dat: Mapped[float] = mapped_column(Float, default=0)
    don_gia_po: Mapped[float] = mapped_column(Float, default=0)
    so_hop_dong: Mapped[str] = mapped_column(String(80), default="")
    ngay_ky: Mapped[date | None] = mapped_column(Date, nullable=True)
    ngay_giao_cam_ket: Mapped[date | None] = mapped_column(Date, nullable=True)
    ngay_nhan_thuc_te: Mapped[date | None] = mapped_column(Date, nullable=True)
    sl_nhan: Mapped[float] = mapped_column(Float, default=0)
    sl_loi: Mapped[float] = mapped_column(Float, default=0)
    sl_tra_lai: Mapped[float] = mapped_column(Float, default=0)
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class ThanhToan(Base):
    """Sheet 'Thanh toán' - sổ chi tiền cho NCC (1 PO có thể chi nhiều đợt)."""
    __tablename__ = "thanh_toan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_phieu_chi: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ngay: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_po: Mapped[str] = mapped_column(String(30), default="")
    so_tien: Mapped[float] = mapped_column(Float, default=0)
    dot: Mapped[float] = mapped_column(Float, default=0)
    hinh_thuc: Mapped[str] = mapped_column(String(60), default="")
    so_chung_tu: Mapped[str] = mapped_column(String(80), default="")
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class NguonDuLieu(Base):
    """Cấu hình kết nối nguồn dữ liệu ngoài (đồng bộ tự động từ URL CSV/JSON)."""
    __tablename__ = "nguon_du_lieu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    url: Mapped[str] = mapped_column(Text, default="")
    dinh_dang: Mapped[str] = mapped_column(String(10), default="csv")  # csv | json
    bat: Mapped[bool] = mapped_column(Boolean, default=False)
    lan_cuoi: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ket_qua_cuoi: Mapped[str] = mapped_column(String(300), default="")


class BaoCaoLuu(Base):
    """Báo cáo Excel đã chốt & lưu (thủ công hoặc theo lịch cuối tháng)."""
    __tablename__ = "bao_cao_luu"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ten: Mapped[str] = mapped_column(String(200))
    ky: Mapped[str] = mapped_column(String(20), index=True)  # vd "2026-07" hoặc "2026"
    thoi_gian: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    so_byte: Mapped[int] = mapped_column(Integer, default=0)
    du_lieu: Mapped[bytes] = mapped_column(LargeBinary)
