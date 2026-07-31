"""Tái hiện các công thức tự động của file mẫu THNG.

Mọi giá trị "chữ đen tự tính" trong Excel được tính ở đây để hiển thị trên web
và để đối chiếu. Khi xuất Excel, ta chỉ điền ô nhập tay còn công thức trong file
mẫu tự tính lại - nên logic ở đây phải khớp với công thức trong file mẫu.
"""
from __future__ import annotations

from datetime import date
from typing import Iterable

from . import models


# ---- Báo giá -------------------------------------------------------------

def gia_sau_vat(bg: models.BaoGia) -> float:
    """Giá sau VAT = Giá trước VAT * (1 + VAT%)."""
    return round((bg.gia_truoc_vat or 0) * (1 + (bg.vat or 0)))


def ten_khach_hang(ma_kh: str, kh_index: dict[str, models.KhachHang]) -> str:
    kh = kh_index.get(ma_kh)
    return kh.ten if kh else ""


# ---- Hợp đồng ------------------------------------------------------------

def tinh_trang_tien_do(hd: models.HopDong, today: date | None = None) -> str:
    """Đúng hạn / Giao trễ / Đang thực hiện / Trễ hạn / Chưa có kế hoạch."""
    today = today or date.today()
    if not hd.ma_po:
        return ""
    if hd.ngay_giao_thuc_te is None:
        if hd.ngay_giao_cam_ket is None:
            return "Chưa có kế hoạch"
        return "Trễ hạn" if today > hd.ngay_giao_cam_ket else "Đang thực hiện"
    if hd.ngay_giao_cam_ket is None:
        return "Đúng hạn"
    return "Đúng hạn" if hd.ngay_giao_thuc_te <= hd.ngay_giao_cam_ket else "Giao trễ"


def so_ngay_tre(hd: models.HopDong, today: date | None = None) -> int:
    today = today or date.today()
    if not hd.ma_po:
        return 0
    if hd.ngay_giao_thuc_te is None:
        if hd.ngay_giao_cam_ket is None:
            return 0
        return max(0, (today - hd.ngay_giao_cam_ket).days)
    if hd.ngay_giao_cam_ket is None:
        return 0
    return max(0, (hd.ngay_giao_thuc_te - hd.ngay_giao_cam_ket).days)


def han_thanh_toan(
    hd: models.HopDong,
    bg_index: dict[str, models.BaoGia],
    kh_index: dict[str, models.KhachHang],
) -> date | None:
    """Hạn thanh toán = Ngày giao thực tế + Điều khoản TT (số ngày) của KH."""
    if not hd.ma_po or hd.ngay_giao_thuc_te is None:
        return None
    ma_kh = ma_kh_cua_po(hd, bg_index)
    kh = kh_index.get(ma_kh)
    ngay_dieu_khoan = kh.dieu_khoan_tt if kh else 0
    from datetime import timedelta

    return hd.ngay_giao_thuc_te + timedelta(days=ngay_dieu_khoan)


def ma_kh_cua_po(hd: models.HopDong, bg_index: dict[str, models.BaoGia]) -> str:
    """Mã KH của hợp đồng lấy qua mã báo giá."""
    bg = bg_index.get(hd.ma_bao_gia)
    return bg.ma_kh if bg else ""


def gia_tri_bao_gia_goc(hd: models.HopDong, bg_index: dict[str, models.BaoGia]) -> float:
    bg = bg_index.get(hd.ma_bao_gia)
    return gia_sau_vat(bg) if bg else 0


# ---- Công nợ (tính theo từng PO) ----------------------------------------

def da_thu_theo_po(ma_po: str, thanh_toans: Iterable[models.ThanhToan]) -> float:
    return sum(tt.so_tien_thu or 0 for tt in thanh_toans if tt.ma_po == ma_po)


def nhom_tuoi_no(con_phai_thu: float, so_ngay_qua_han: int) -> str:
    if con_phai_thu <= 0:
        return "Đã thu đủ"
    if so_ngay_qua_han == 0:
        return "Trong hạn"
    if so_ngay_qua_han <= 30:
        return "Quá hạn 1-30 ngày"
    if so_ngay_qua_han <= 60:
        return "Quá hạn 31-60 ngày"
    if so_ngay_qua_han <= 90:
        return "Quá hạn 61-90 ngày"
    return "Quá hạn trên 90 ngày"


def cong_no_theo_po(
    hd: models.HopDong,
    thanh_toans: list[models.ThanhToan],
    bg_index: dict[str, models.BaoGia],
    kh_index: dict[str, models.KhachHang],
    today: date | None = None,
) -> dict:
    """Trả về dòng công nợ của một PO, giống sheet 'Công nợ'."""
    today = today or date.today()
    gia_tri = hd.gia_tri_hop_dong or 0
    da_thu = da_thu_theo_po(hd.ma_po, thanh_toans)
    con_phai_thu = gia_tri - da_thu
    han = han_thanh_toan(hd, bg_index, kh_index)
    if con_phai_thu <= 0 or han is None:
        qua_han = 0
    else:
        qua_han = max(0, (today - han).days)
    return {
        "ma_po": hd.ma_po,
        "khach_hang": ten_khach_hang(ma_kh_cua_po(hd, bg_index), kh_index),
        "gia_tri_hop_dong": gia_tri,
        "da_thu": da_thu,
        "con_phai_thu": con_phai_thu,
        "han_thanh_toan": han,
        "so_ngay_qua_han": qua_han,
        "nhom_tuoi_no": nhom_tuoi_no(con_phai_thu, qua_han),
        "phan_tram_da_thu": (da_thu / gia_tri) if gia_tri else 0,
    }


# ---- Tổng quan (KPI dashboard) ------------------------------------------

def tong_quan(
    khachs: list[models.KhachHang],
    bao_gias: list[models.BaoGia],
    hop_dongs: list[models.HopDong],
    thanh_toans: list[models.ThanhToan],
    today: date | None = None,
) -> dict:
    today = today or date.today()
    bg_index = {b.ma_bao_gia: b for b in bao_gias}
    kh_index = {k.ma_kh: k for k in khachs}

    so_bao_gia = len(bao_gias)
    tong_gt_bao_gia = sum(gia_sau_vat(b) for b in bao_gias)
    gt_thang = sum(gia_sau_vat(b) for b in bao_gias if b.trang_thai == "Thắng")
    ty_le_thang = (gt_thang / tong_gt_bao_gia) if tong_gt_bao_gia else 0

    so_hd = len(hop_dongs)
    tong_gt_hd = sum(h.gia_tri_hop_dong or 0 for h in hop_dongs)

    cong_nos = [
        cong_no_theo_po(h, thanh_toans, bg_index, kh_index, today) for h in hop_dongs
    ]
    da_thu = sum(c["da_thu"] for c in cong_nos)
    con_phai_thu = sum(c["con_phai_thu"] for c in cong_nos)
    no_qua_han = sum(
        c["con_phai_thu"] for c in cong_nos if c["so_ngay_qua_han"] > 0
    )

    po_tre_han = sum(
        1 for h in hop_dongs if tinh_trang_tien_do(h, today) == "Trễ hạn"
    )
    po_loi = sum(1 for h in hop_dongs if h.tinh_trang_chat_luong == "Lỗi")

    # tỷ lệ giao đúng hạn: trong các PO đã giao
    da_giao = [h for h in hop_dongs if h.ngay_giao_thuc_te is not None]
    dung_han = sum(
        1 for h in da_giao if tinh_trang_tien_do(h, today) == "Đúng hạn"
    )
    ty_le_giao_dung_han = (dung_han / len(da_giao)) if da_giao else 0

    return {
        "nam": today.year,
        "so_bao_gia": so_bao_gia,
        "tong_gt_bao_gia": tong_gt_bao_gia,
        "gt_thang": gt_thang,
        "ty_le_thang": ty_le_thang,
        "so_hop_dong": so_hd,
        "tong_gt_hop_dong": tong_gt_hd,
        "da_thu": da_thu,
        "con_phai_thu": con_phai_thu,
        "no_qua_han": no_qua_han,
        "po_tre_han": po_tre_han,
        "po_loi": po_loi,
        "ty_le_giao_dung_han": ty_le_giao_dung_han,
        "so_khach_hang": len(khachs),
    }


# ---- Dữ liệu cho biểu đồ (Giai đoạn 3) ----------------------------------

def dien_bien_thang(hop_dongs, thanh_toans) -> list[dict]:
    """Số liệu 12 tháng: giá trị HĐ ký & tiền thu (theo tháng của dữ liệu đã lọc)."""
    gt = [0.0] * 12
    thu = [0.0] * 12
    for h in hop_dongs:
        if h.ngay_ky:
            gt[h.ngay_ky.month - 1] += h.gia_tri_hop_dong or 0
    for t in thanh_toans:
        if t.ngay_thu:
            thu[t.ngay_thu.month - 1] += t.so_tien_thu or 0
    return [{"thang": m + 1, "gt_hd_ky": gt[m], "tien_thu": thu[m]} for m in range(12)]


# Thứ tự nhóm tuổi nợ (từ nhẹ đến nặng), để vẽ biểu đồ công nợ
NHOM_TUOI_NO = [
    "Trong hạn", "Quá hạn 1-30 ngày", "Quá hạn 31-60 ngày",
    "Quá hạn 61-90 ngày", "Quá hạn trên 90 ngày",
]


def co_cau_tuoi_no(khachs, bao_gias, hop_dongs, thanh_toans,
                   today: date | None = None) -> list[dict]:
    """Tổng 'còn phải thu' theo từng nhóm tuổi nợ (bỏ nhóm đã thu đủ)."""
    today = today or date.today()
    bg_index = {b.ma_bao_gia: b for b in bao_gias}
    kh_index = {k.ma_kh: k for k in khachs}
    tong = {n: 0.0 for n in NHOM_TUOI_NO}
    for h in hop_dongs:
        c = cong_no_theo_po(h, thanh_toans, bg_index, kh_index, today)
        nhom = c["nhom_tuoi_no"]
        if nhom in tong:
            tong[nhom] += c["con_phai_thu"]
    return [{"nhom": n, "so_tien": tong[n]} for n in NHOM_TUOI_NO]
