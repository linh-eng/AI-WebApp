"""Khởi tạo dữ liệu lần đầu: tài khoản admin + chuỗi dữ liệu mẫu để xem ngay.

Chuỗi mẫu nối tiếp đúng quy trình:
  DA-2026-01 -> YC-2026-001 -> BG-2026-001 (NCC001, được chọn) -> PR-2026-001
  -> PO-2026-001 -> PC-2026-001
"""
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
        if db.scalar(select(func.count()).select_from(models.DuAn)) == 0:
            db.add(models.DuAn(
                ma_du_an="DA-2026-01", ten="Nhà máy Bao bì Tân Uyên – Giai đoạn 1",
                khach_hang="Công ty CP Bao bì Tân Uyên", pm="Phạm Minh Đức",
                ngay_bat_dau=date(2026, 1, 2), ngay_ket_thuc=date(2026, 9, 30),
                ngan_sach=5_000_000_000, trang_thai="Đang thực hiện",
                ghi_chu="Dự án mẫu"))
            db.add(models.NhaCungCap(
                ma_ncc="NCC001", ten="Công ty TNHH Thép Việt An",
                nguoi_lien_he="Nguyễn Văn Bình", dien_thoai="0901234567",
                email="binh.nv@vietan.com.vn", dia_chi="12 Lê Lợi, Q.1, TP.HCM",
                dieu_khoan_tt=30, danh_gia="A", nhom_hang="Thép tấm, thép hình",
                ma_so_thue="0301234567", ghi_chu="NCC mẫu"))
            db.add(models.NhaCungCap(
                ma_ncc="NCC002", ten="Công ty CP Vật tư Miền Nam",
                nguoi_lien_he="Lê Thị Hoa", dien_thoai="0912345678",
                email="hoa.lt@vtmn.vn", dieu_khoan_tt=45, danh_gia="B",
                nhom_hang="Vật tư phụ", ma_so_thue="0312345678"))
            db.add(models.CheckGia(
                ma_yc="YC-2026-001", ngay_nhan=date(2026, 1, 3), ma_du_an="DA-2026-01",
                nguoi_yc="Phòng Dự án – Trần Văn Nam",
                hang_muc="Thép tấm SS400 dày 10mm (1500x6000)", dvt="Tấm",
                so_luong=200, don_gia_du_toan=1_250_000,
                han_tra_gia=date(2026, 1, 9), ngay_tra_gia=date(2026, 1, 8),
                trang_thai="Đã trả giá"))
            db.add(models.BaoGia(
                ma_bao_gia="BG-2026-001", ngay=date(2026, 1, 8), ma_yc="YC-2026-001",
                ma_ncc="NCC001", don_gia=1_180_000, thoi_gian_giao=20,
                hieu_luc=date(2026, 2, 8), duoc_chon="x"))
            db.add(models.BaoGia(
                ma_bao_gia="BG-2026-002", ngay=date(2026, 1, 8), ma_yc="YC-2026-001",
                ma_ncc="NCC002", don_gia=1_240_000, thoi_gian_giao=25,
                hieu_luc=date(2026, 2, 8), duoc_chon=""))
            db.add(models.PR(
                ma_pr="PR-2026-001", ngay=date(2026, 1, 12), ma_yc="YC-2026-001",
                so_luong=200, don_gia_du_toan=1_250_000,
                ngay_can_hang=date(2026, 2, 20), trang_thai_duyet="Đã duyệt",
                nguoi_duyet="Giám đốc Dự án", ngay_duyet=date(2026, 1, 13)))
            db.add(models.PO(
                ma_po="PO-2026-001", ngay=date(2026, 1, 15), ma_pr="PR-2026-001",
                ma_ncc="NCC001", so_luong_dat=200, don_gia_po=1_180_000,
                so_hop_dong="05/2026/HĐMB-THNG", ngay_ky=date(2026, 1, 14),
                ngay_giao_cam_ket=date(2026, 2, 15), ngay_nhan_thuc_te=date(2026, 2, 18),
                sl_nhan=200, sl_loi=3, sl_tra_lai=3))
            db.add(models.ThanhToan(
                ma_phieu_chi="PC-2026-001", ngay=date(2026, 2, 20), ma_po="PO-2026-001",
                so_tien=100_000_000, dot=1, hinh_thuc="Chuyển khoản",
                so_chung_tu="UNC 0125", ghi_chu="Tạm ứng đợt 1"))
            db.commit()
    finally:
        db.close()
