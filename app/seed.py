"""Khởi tạo dữ liệu lần đầu: tài khoản admin + vài dòng dữ liệu mẫu để xem ngay."""
from datetime import date

from sqlalchemy import func, select

from . import models
from .config import ADMIN_PASSWORD, ADMIN_USERNAME
from .database import SessionLocal
from .security import hash_password


def khoi_tao_du_lieu():
    db = SessionLocal()
    try:
        # Tài khoản admin
        if not db.scalar(select(models.NguoiDung).where(
                models.NguoiDung.username == ADMIN_USERNAME)):
            db.add(models.NguoiDung(
                username=ADMIN_USERNAME,
                mat_khau_hash=hash_password(ADMIN_PASSWORD),
                ho_ten="Quản trị viên",
                vai_tro="admin",
            ))
            db.commit()

        # Dữ liệu mẫu (chỉ nạp khi CSDL còn trống)
        if db.scalar(select(func.count()).select_from(models.KhachHang)) == 0:
            db.add(models.KhachHang(
                ma_kh="KH001", ten="Công ty TNHH ABC", nguoi_lien_he="Trần Thị B",
                lien_he="0901234567", dieu_khoan_tt=30, han_muc_cong_no=500_000_000,
                ghi_chu="Khách hàng mẫu"))
            db.add(models.BaoGia(
                ma_bao_gia="BG2026-001", ngay=date(2026, 1, 5), ma_kh="KH001",
                noi_dung="Cung cấp vật tư theo YCKH", gia_truoc_vat=250_000_000,
                vat=0.08, hieu_luc_den=date(2026, 2, 5), trang_thai="Thắng",
                ma_po="PO2026-001", nv_phu_trach="Nguyễn Văn A"))
            db.add(models.HopDong(
                ma_po="PO2026-001", ngay_nhan_po=date(2026, 1, 10),
                ma_bao_gia="BG2026-001", so_hop_dong="HĐ01/2026",
                ngay_ky=date(2026, 1, 12), gia_tri_hop_dong=270_000_000,
                ngay_giao_cam_ket=date(2026, 2, 15),
                ngay_giao_thuc_te=date(2026, 2, 14),
                tinh_trang_chat_luong="Đạt", ty_le_hang_loi=0))
            db.add(models.ThanhToan(
                ma_phieu_thu="PT2026-001", ngay_thu=date(2026, 1, 20),
                ma_po="PO2026-001", so_tien_thu=135_000_000,
                hinh_thuc="Chuyển khoản", dot_noi_dung="Tạm ứng 50%"))
            db.commit()
    finally:
        db.close()
