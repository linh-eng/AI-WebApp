"""Mô hình dữ liệu - khớp với các sheet nhập tay của file mẫu THNG.

Quy trình: Báo giá -> PO/Hợp đồng -> Thanh toán -> Công nợ (tính động).
Chỉ lưu dữ liệu NHẬP TAY; các giá trị công thức (tên KH, giá sau VAT, công nợ,
tình trạng tiến độ...) được tính động ở tầng calculations.py.
"""
from datetime import date, datetime

from sqlalchemy import (Boolean, Date, DateTime, Float, Integer, LargeBinary,
                        String, Text)
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


class KhachHang(Base):
    """Sheet 'Khách hàng' - toàn bộ nhập tay."""
    __tablename__ = "khach_hang"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_kh: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    ten: Mapped[str] = mapped_column(String(200))
    nguoi_lien_he: Mapped[str] = mapped_column(String(120), default="")
    lien_he: Mapped[str] = mapped_column(String(120), default="")  # ĐT/Email
    dieu_khoan_tt: Mapped[int] = mapped_column(Integer, default=0)  # số ngày
    han_muc_cong_no: Mapped[float] = mapped_column(Float, default=0)
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class BaoGia(Base):
    """Sheet 'Báo giá'."""
    __tablename__ = "bao_gia"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_bao_gia: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    ngay: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_kh: Mapped[str] = mapped_column(String(30), default="")
    noi_dung: Mapped[str] = mapped_column(String(400), default="")
    gia_truoc_vat: Mapped[float] = mapped_column(Float, default=0)
    vat: Mapped[float] = mapped_column(Float, default=0.08)  # phân số, vd 0.08 = 8%
    hieu_luc_den: Mapped[date | None] = mapped_column(Date, nullable=True)
    trang_thai: Mapped[str] = mapped_column(String(20), default="Đang chào")
    ma_po: Mapped[str] = mapped_column(String(40), default="")  # điền khi thắng
    nv_phu_trach: Mapped[str] = mapped_column(String(120), default="")
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class HopDong(Base):
    """Sheet 'Hợp đồng' - PO / Hợp đồng / Tiến độ / Chất lượng."""
    __tablename__ = "hop_dong"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_po: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    ngay_nhan_po: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_bao_gia: Mapped[str] = mapped_column(String(40), default="")
    so_hop_dong: Mapped[str] = mapped_column(String(60), default="")
    ngay_ky: Mapped[date | None] = mapped_column(Date, nullable=True)
    gia_tri_hop_dong: Mapped[float] = mapped_column(Float, default=0)
    ngay_giao_cam_ket: Mapped[date | None] = mapped_column(Date, nullable=True)
    ngay_giao_thuc_te: Mapped[date | None] = mapped_column(Date, nullable=True)
    tinh_trang_chat_luong: Mapped[str] = mapped_column(String(20), default="")  # Đạt/Lỗi
    ty_le_hang_loi: Mapped[float] = mapped_column(Float, default=0)
    ghi_chu: Mapped[str] = mapped_column(String(300), default="")


class ThanhToan(Base):
    """Sheet 'Thanh toán' - sổ thu tiền (1 PO có thể thu nhiều đợt)."""
    __tablename__ = "thanh_toan"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_phieu_thu: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    ngay_thu: Mapped[date | None] = mapped_column(Date, nullable=True)
    ma_po: Mapped[str] = mapped_column(String(40), default="")
    so_tien_thu: Mapped[float] = mapped_column(Float, default=0)
    hinh_thuc: Mapped[str] = mapped_column(String(60), default="")
    dot_noi_dung: Mapped[str] = mapped_column(String(200), default="")


class NguonDuLieu(Base):
    """Cấu hình kết nối nguồn dữ liệu ngoài (Giai đoạn 3).

    Mỗi màn hình (khach-hang/bao-gia/hop-dong/thanh-toan) có thể đồng bộ tự động
    từ một URL trả về CSV hoặc JSON (vd Google Sheets publish-to-web, hoặc endpoint
    xuất dữ liệu của phần mềm bán hàng/ERP công ty).
    """
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
