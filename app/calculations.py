"""Tái hiện các công thức tự động của file mẫu Báo cáo Mua hàng THNG.

Mọi giá trị "tự tính" trong Excel được tính lại ở đây để hiển thị trên web và
để đối chiếu. Khi xuất Excel, ta chỉ điền ô nhập tay; công thức trong file mẫu
tự tính lại - nên logic ở đây phải khớp công thức file mẫu.

Chuỗi liên kết dữ liệu:
    Dự án ─┐
           ├─ Check giá (YC) ──┬─ Báo giá (nhiều NCC, chọn 1)
           │                   └─ PR ── PO ──┬─ Thanh toán
    NCC ───┘                                 └─ Công nợ (động)
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

from . import models
from .config import NGUONG_HANG_LOI


# ---- Chỉ mục tra cứu -----------------------------------------------------

def _index(records, attr):
    return {getattr(r, attr): r for r in records}


# ---- Check giá -----------------------------------------------------------

def cg_gia_tri_du_toan(cg: models.CheckGia) -> float:
    return (cg.so_luong or 0) * (cg.don_gia_du_toan or 0)


def cg_so_ngay_xu_ly(cg: models.CheckGia) -> int | None:
    if cg.ngay_tra_gia and cg.ngay_nhan:
        return (cg.ngay_tra_gia - cg.ngay_nhan).days
    return None


def cg_sla(cg: models.CheckGia, today: date | None = None) -> str:
    """Khớp công thức 'Check giá'!O: Đúng hạn / Trả trễ / Đang xử lý / Quá hạn chưa trả."""
    today = today or date.today()
    if cg.han_tra_gia is None:
        return ""
    if cg.ngay_tra_gia is None:
        return "Quá hạn chưa trả" if today > cg.han_tra_gia else "Đang xử lý"
    return "Đúng hạn" if cg.ngay_tra_gia <= cg.han_tra_gia else "Trả trễ"


def cg_bao_gia_duoc_chon(cg: models.CheckGia, bao_gias: Iterable[models.BaoGia]):
    for b in bao_gias:
        if b.ma_yc == cg.ma_yc and (b.duoc_chon or "").strip().lower() == "x":
            return b
    return None


def cg_don_gia_chot(cg: models.CheckGia, bao_gias) -> float:
    b = cg_bao_gia_duoc_chon(cg, bao_gias)
    return (b.don_gia or 0) if b else 0


def cg_gia_tri_chot(cg: models.CheckGia, bao_gias) -> float:
    return cg_don_gia_chot(cg, bao_gias) * (cg.so_luong or 0)


def cg_so_ncc_bao_gia(cg: models.CheckGia, bao_gias) -> int:
    return sum(1 for b in bao_gias if b.ma_yc == cg.ma_yc)


# ---- Báo giá -------------------------------------------------------------

def bg_thanh_tien(bg: models.BaoGia, cg_index: dict) -> float:
    cg = cg_index.get(bg.ma_yc)
    so_luong = (cg.so_luong or 0) if cg else 0
    return so_luong * (bg.don_gia or 0)


# ---- PR ------------------------------------------------------------------

def pr_gia_tri_du_toan(pr: models.PR) -> float:
    return (pr.so_luong or 0) * (pr.don_gia_du_toan or 0)


# ---- PO ------------------------------------------------------------------

def po_gia_tri(po: models.PO) -> float:
    return (po.so_luong_dat or 0) * (po.don_gia_po or 0)


def po_du_toan_pr(po: models.PO, pr_index: dict) -> float:
    pr = pr_index.get(po.ma_pr)
    return pr_gia_tri_du_toan(pr) if pr else 0


def po_tiet_kiem(po: models.PO, pr_index: dict) -> float:
    return po_du_toan_pr(po, pr_index) - po_gia_tri(po)


def po_danh_gia_giao(po: models.PO, today: date | None = None) -> str:
    """Khớp 'PO'!S: Đúng hạn / Giao trễ / Trễ hạn / Chưa đến hạn."""
    today = today or date.today()
    if po.ngay_giao_cam_ket is None:
        return ""
    if po.ngay_nhan_thuc_te is None:
        return "Trễ hạn" if today > po.ngay_giao_cam_ket else "Chưa đến hạn"
    return "Đúng hạn" if po.ngay_nhan_thuc_te <= po.ngay_giao_cam_ket else "Giao trễ"


def po_so_ngay_tre(po: models.PO, today: date | None = None) -> int:
    today = today or date.today()
    if po.ngay_giao_cam_ket is None:
        return 0
    if po.ngay_nhan_thuc_te is None:
        return (today - po.ngay_giao_cam_ket).days if today > po.ngay_giao_cam_ket else 0
    return max(0, (po.ngay_nhan_thuc_te - po.ngay_giao_cam_ket).days)


def po_ty_le_loi(po: models.PO) -> float:
    return (po.sl_loi or 0) / (po.sl_nhan or 0) if (po.sl_nhan or 0) else 0


def po_ket_qua_cl(po: models.PO) -> str:
    """Khớp 'PO'!Y: Đạt nếu tỷ lệ lỗi <= ngưỡng, ngược lại Không đạt."""
    if not (po.sl_nhan or 0):
        return ""
    return "Đạt" if po_ty_le_loi(po) <= NGUONG_HANG_LOI else "Không đạt"


def po_dieu_khoan_tt(po: models.PO, ncc_index: dict) -> int:
    ncc = ncc_index.get(po.ma_ncc)
    return (ncc.dieu_khoan_tt or 0) if ncc else 0


def po_han_thanh_toan(po: models.PO, ncc_index: dict) -> date | None:
    if po.ngay_nhan_thuc_te is None:
        return None
    return po.ngay_nhan_thuc_te + timedelta(days=po_dieu_khoan_tt(po, ncc_index))


# ---- Thanh toán / Công nợ ------------------------------------------------

def da_tra_theo_po(ma_po: str, thanh_toans: Iterable[models.ThanhToan]) -> float:
    return sum(t.so_tien or 0 for t in thanh_toans if t.ma_po == ma_po)


def nhom_tuoi_no(con_phai_tra: float, so_ngay_qua_han: int) -> str:
    if con_phai_tra <= 0:
        return "Đã thanh toán"
    if so_ngay_qua_han == 0:
        return "Trong hạn"
    if so_ngay_qua_han <= 30:
        return "Quá hạn 1-30 ngày"
    if so_ngay_qua_han <= 60:
        return "Quá hạn 31-60 ngày"
    if so_ngay_qua_han <= 90:
        return "Quá hạn 61-90 ngày"
    return "Quá hạn trên 90 ngày"


def cong_no_theo_po(po: models.PO, thanh_toans, ncc_index, today: date | None = None) -> dict:
    """Một dòng công nợ của 1 PO, khớp sheet 'Công nợ'."""
    today = today or date.today()
    gia_tri = po_gia_tri(po)
    da_tra = da_tra_theo_po(po.ma_po, thanh_toans)
    con = gia_tri - da_tra
    han = po_han_thanh_toan(po, ncc_index)
    if con <= 0 or han is None:
        qua_han = 0
    else:
        qua_han = max(0, (today - han).days)
    ncc = ncc_index.get(po.ma_ncc)
    if con <= 0:
        trang_thai = "Đã thanh toán đủ"
    elif qua_han > 0:
        trang_thai = "QUÁ HẠN"
    else:
        trang_thai = "Còn nợ, trong hạn"
    return {
        "ma_po": po.ma_po,
        "ma_ncc": po.ma_ncc,
        "ten_ncc": ncc.ten if ncc else "",
        "gia_tri_po": gia_tri,
        "da_thanh_toan": da_tra,
        "con_phai_tra": con,
        "han_thanh_toan": han,
        "so_ngay_qua_han": qua_han,
        "nhom_tuoi_no": nhom_tuoi_no(con, qua_han),
        "trang_thai": trang_thai,
    }


def danh_sach_cong_no(pos, thanh_toans, nhas, today: date | None = None) -> list[dict]:
    ncc_index = _index(nhas, "ma_ncc")
    return [cong_no_theo_po(p, thanh_toans, ncc_index, today) for p in pos]


# ---- Tổng quan (KPI dashboard) ------------------------------------------

def tong_quan(du_ans, nhas, check_gias, bao_gias, prs, pos, thanh_toans,
              today: date | None = None) -> dict:
    """Toàn bộ KPI của sheet 'Tổng quan', chia 6 nhóm A-F."""
    today = today or date.today()
    cg_index = _index(check_gias, "ma_yc")
    pr_index = _index(prs, "ma_pr")
    ncc_index = _index(nhas, "ma_ncc")

    # A. Tiếp nhận & xử lý yêu cầu check giá
    so_yc = len(check_gias)
    so_yc_da_tra = sum(1 for c in check_gias if (c.trang_thai or "") == "Đã trả giá")
    slas = [cg_sla(c, today) for c in check_gias]
    so_yc_dang_xu_ly = sum(1 for s in slas if s == "Đang xử lý")
    so_yc_qua_han = sum(1 for s in slas if s == "Quá hạn chưa trả")
    dung_han = sum(1 for s in slas if s == "Đúng hạn")
    tra_tre = sum(1 for s in slas if s == "Trả trễ")
    sla_dung_han = dung_han / (dung_han + tra_tre) if (dung_han + tra_tre) else 0
    ngay_xl = [cg_so_ngay_xu_ly(c) for c in check_gias]
    ngay_xl = [d for d in ngay_xl if d is not None]
    tg_xu_ly_bq = sum(ngay_xl) / len(ngay_xl) if ngay_xl else 0
    tong_du_toan_yc = sum(cg_gia_tri_du_toan(c) for c in check_gias)
    tong_gia_chot = sum(cg_gia_tri_chot(c, bao_gias) for c in check_gias)
    chenh_lech_chot = tong_gia_chot - tong_du_toan_yc

    # B. PR - PO - Hợp đồng
    so_pr = len(prs)
    so_pr_duyet = sum(1 for p in prs if (p.trang_thai_duyet or "") == "Đã duyệt")
    tong_dutoan_pr = sum(pr_gia_tri_du_toan(p) for p in prs)
    so_po = len(pos)
    tong_gt_po = sum(po_gia_tri(p) for p in pos)
    dutoan_pr_ra_po = sum(po_du_toan_pr(p, pr_index) for p in pos)
    tiet_kiem = sum(po_tiet_kiem(p, pr_index) for p in pos)
    ty_le_tiet_kiem = tiet_kiem / dutoan_pr_ra_po if dutoan_pr_ra_po else 0

    # C. Tiến độ giao hàng & chất lượng
    danh_gia = [po_danh_gia_giao(p, today) for p in pos]
    po_den_han = sum(1 for d in danh_gia if d in ("Đúng hạn", "Giao trễ", "Trễ hạn"))
    po_dung_han = sum(1 for d in danh_gia if d == "Đúng hạn")
    po_giao_tre = sum(1 for d in danh_gia if d == "Giao trễ")
    po_tre_han = sum(1 for d in danh_gia if d == "Trễ hạn")
    ty_le_giao_dung_han = po_dung_han / po_den_han if po_den_han else 0
    kq_cl = [po_ket_qua_cl(p) for p in pos]
    po_kiem_cl = sum(1 for k in kq_cl if k in ("Đạt", "Không đạt"))
    po_dat = sum(1 for k in kq_cl if k == "Đạt")
    ty_le_dat = po_dat / po_kiem_cl if po_kiem_cl else 0
    tong_nhan = sum(p.sl_nhan or 0 for p in pos)
    tong_loi = sum(p.sl_loi or 0 for p in pos)
    ty_le_loi_bq = tong_loi / tong_nhan if tong_nhan else 0

    # D. Thanh toán & công nợ phải trả
    cong_nos = [cong_no_theo_po(p, thanh_toans, ncc_index, today) for p in pos]
    da_thanh_toan = sum(t.so_tien or 0 for t in thanh_toans)
    con_phai_tra = sum(c["con_phai_tra"] for c in cong_nos)
    no_qua_han = sum(c["con_phai_tra"] for c in cong_nos if c["so_ngay_qua_han"] > 0)
    ty_le_no_qua_han = no_qua_han / con_phai_tra if con_phai_tra else 0

    # E. Tuổi nợ quá hạn (aging)
    def _aging(lo, hi):
        return sum(c["con_phai_tra"] for c in cong_nos
                   if lo <= c["so_ngay_qua_han"] <= hi and c["con_phai_tra"] > 0)
    no_1_30 = _aging(1, 30)
    no_31_60 = _aging(31, 60)
    no_61_90 = _aging(61, 90)
    no_90 = sum(c["con_phai_tra"] for c in cong_nos
                if c["so_ngay_qua_han"] > 90 and c["con_phai_tra"] > 0)
    tong_qua_han = no_1_30 + no_31_60 + no_61_90 + no_90
    no_trong_han = sum(c["con_phai_tra"] for c in cong_nos
                       if c["so_ngay_qua_han"] == 0 and c["con_phai_tra"] > 0)

    # F. Dự án
    so_du_an = len(du_ans)
    dang_thuc_hien = sum(1 for d in du_ans if (d.trang_thai or "") == "Đang thực hiện")
    tong_ngan_sach = sum(d.ngan_sach or 0 for d in du_ans)
    ty_le_su_dung = tong_gt_po / tong_ngan_sach if tong_ngan_sach else 0
    ngan_sach_con_lai = tong_ngan_sach - tong_gt_po

    return {
        "nam": today.year,
        # A
        "so_yc": so_yc, "so_yc_da_tra": so_yc_da_tra,
        "so_yc_dang_xu_ly": so_yc_dang_xu_ly, "so_yc_qua_han": so_yc_qua_han,
        "sla_dung_han": sla_dung_han, "tg_xu_ly_bq": tg_xu_ly_bq,
        "tong_du_toan_yc": tong_du_toan_yc, "tong_gia_chot": tong_gia_chot,
        "chenh_lech_chot": chenh_lech_chot,
        # B
        "so_pr": so_pr, "so_pr_duyet": so_pr_duyet, "tong_dutoan_pr": tong_dutoan_pr,
        "so_po": so_po, "tong_gt_po": tong_gt_po, "tiet_kiem": tiet_kiem,
        "ty_le_tiet_kiem": ty_le_tiet_kiem,
        # C
        "po_den_han": po_den_han, "po_dung_han": po_dung_han,
        "po_giao_tre": po_giao_tre, "po_tre_han": po_tre_han,
        "ty_le_giao_dung_han": ty_le_giao_dung_han,
        "po_kiem_cl": po_kiem_cl, "po_dat": po_dat, "ty_le_dat": ty_le_dat,
        "ty_le_loi_bq": ty_le_loi_bq,
        # D
        "da_thanh_toan": da_thanh_toan, "con_phai_tra": con_phai_tra,
        "no_qua_han": no_qua_han, "ty_le_no_qua_han": ty_le_no_qua_han,
        # E
        "no_1_30": no_1_30, "no_31_60": no_31_60, "no_61_90": no_61_90, "no_90": no_90,
        "tong_qua_han": tong_qua_han, "no_trong_han": no_trong_han,
        # F
        "so_du_an": so_du_an, "dang_thuc_hien": dang_thuc_hien,
        "tong_ngan_sach": tong_ngan_sach, "ty_le_su_dung": ty_le_su_dung,
        "ngan_sach_con_lai": ngan_sach_con_lai,
        "so_ncc": len(nhas),
    }


# ---- Dữ liệu cho biểu đồ -------------------------------------------------

def dien_bien_thang(pos, thanh_toans) -> list[dict]:
    """12 tháng: giá trị PO phát hành (theo Ngày PO) & tiền chi (theo Ngày TT)."""
    gt = [0.0] * 12
    chi = [0.0] * 12
    for p in pos:
        if p.ngay:
            gt[p.ngay.month - 1] += po_gia_tri(p)
    for t in thanh_toans:
        if t.ngay:
            chi[t.ngay.month - 1] += t.so_tien or 0
    return [{"thang": m + 1, "gt_hd_ky": gt[m], "tien_thu": chi[m]} for m in range(12)]


NHOM_TUOI_NO = [
    "Trong hạn", "Quá hạn 1-30 ngày", "Quá hạn 31-60 ngày",
    "Quá hạn 61-90 ngày", "Quá hạn trên 90 ngày",
]


def co_cau_tuoi_no(pos, thanh_toans, nhas, today: date | None = None) -> list[dict]:
    """Tổng 'còn phải trả' theo từng nhóm tuổi nợ (bỏ nhóm đã thanh toán đủ)."""
    ncc_index = _index(nhas, "ma_ncc")
    tong = {n: 0.0 for n in NHOM_TUOI_NO}
    for p in pos:
        c = cong_no_theo_po(p, thanh_toans, ncc_index, today)
        if c["nhom_tuoi_no"] in tong:
            tong[c["nhom_tuoi_no"]] += c["con_phai_tra"]
    return [{"nhom": n, "so_tien": tong[n]} for n in NHOM_TUOI_NO]


# ---- Nhắc việc & cảnh báo (Cần xử lý) -----------------------------------

def canh_bao(du_ans, nhas, check_gias, bao_gias, prs, pos, thanh_toans,
             today: date | None = None) -> dict:
    """Việc cần xử lý: nợ NCC quá hạn, YC quá hạn chưa trả giá, PO trễ giao."""
    today = today or date.today()
    ncc_index = _index(nhas, "ma_ncc")

    no_qua_han = []
    for p in pos:
        c = cong_no_theo_po(p, thanh_toans, ncc_index, today)
        if c["con_phai_tra"] > 0 and c["so_ngay_qua_han"] > 0:
            no_qua_han.append(c)
    no_qua_han.sort(key=lambda c: c["so_ngay_qua_han"], reverse=True)

    yc_qua_han = []
    for c in check_gias:
        if cg_sla(c, today) == "Quá hạn chưa trả":
            yc_qua_han.append({
                "ma_yc": c.ma_yc, "hang_muc": c.hang_muc,
                "han_tra_gia": c.han_tra_gia,
                "so_ngay_tre": (today - c.han_tra_gia).days if c.han_tra_gia else 0,
            })
    yc_qua_han.sort(key=lambda x: x["so_ngay_tre"], reverse=True)

    po_tre = []
    for p in pos:
        if po_danh_gia_giao(p, today) == "Trễ hạn":
            ncc = ncc_index.get(p.ma_ncc)
            po_tre.append({
                "ma_po": p.ma_po, "ten_ncc": ncc.ten if ncc else "",
                "ngay_giao_cam_ket": p.ngay_giao_cam_ket,
                "so_ngay_tre": po_so_ngay_tre(p, today),
            })
    po_tre.sort(key=lambda x: x["so_ngay_tre"], reverse=True)

    return {
        "no_qua_han": no_qua_han,
        "yc_qua_han": yc_qua_han,
        "po_tre": po_tre,
        "tong": len(no_qua_han) + len(yc_qua_han) + len(po_tre),
    }


# ---- Dự án của một PO (qua PR -> YC) -------------------------------------

def du_an_cua_po(po: models.PO, pr_index: dict, cg_index: dict) -> str:
    pr = pr_index.get(po.ma_pr)
    if not pr:
        return ""
    cg = cg_index.get(pr.ma_yc)
    return cg.ma_du_an if cg else ""


# ---- So sánh báo giá theo 1 Yêu cầu check giá ---------------------------

def so_sanh_bao_gia(cg: models.CheckGia, bao_gias, nhas) -> list[dict]:
    """Các báo giá của 1 YC, kèm cột tự tính để so sánh và chọn NCC."""
    ncc_index = _index(nhas, "ma_ncc")
    nhom = [b for b in bao_gias if b.ma_yc == cg.ma_yc]
    so_luong = cg.so_luong or 0
    du_toan = cg_gia_tri_du_toan(cg)
    thanh_tiens = [(so_luong * (b.don_gia or 0)) for b in nhom]
    thap_nhat = min(thanh_tiens) if thanh_tiens else 0
    rows = []
    for b in nhom:
        ncc = ncc_index.get(b.ma_ncc)
        tt = so_luong * (b.don_gia or 0)
        rows.append({
            "ma_bao_gia": b.ma_bao_gia, "ma_ncc": b.ma_ncc,
            "ten_ncc": ncc.ten if ncc else "", "danh_gia_ncc": ncc.danh_gia if ncc else "",
            "don_gia": b.don_gia or 0, "thanh_tien": tt,
            "thoi_gian_giao": b.thoi_gian_giao or 0,
            "dieu_khoan_tt": ncc.dieu_khoan_tt if ncc else 0,
            "hieu_luc": b.hieu_luc,
            "chenh_thap_nhat": tt - thap_nhat,
            "chenh_du_toan": tt - du_toan,
            "phan_tram_du_toan": (tt - du_toan) / du_toan if du_toan else 0,
            "la_thap_nhat": tt == thap_nhat and thanh_tiens,
            "duoc_chon": (b.duoc_chon or "").strip().lower() == "x",
        })
    rows.sort(key=lambda r: (not r["duoc_chon"], r["thanh_tien"]))
    return rows


# ---- Thống kê nhà cung cấp ----------------------------------------------

def thong_ke_ncc(nhas, bao_gias, pos, thanh_toans, today: date | None = None) -> list[dict]:
    ncc_index = _index(nhas, "ma_ncc")
    rows = []
    for ncc in nhas:
        bg = [b for b in bao_gias if b.ma_ncc == ncc.ma_ncc]
        so_chon = sum(1 for b in bg if (b.duoc_chon or "").strip().lower() == "x")
        ncc_pos = [p for p in pos if p.ma_ncc == ncc.ma_ncc]
        gia_tri_mua = sum(po_gia_tri(p) for p in ncc_pos)
        dg = [po_danh_gia_giao(p, today) for p in ncc_pos]
        den_han = sum(1 for d in dg if d in ("Đúng hạn", "Giao trễ", "Trễ hạn"))
        dung_han = sum(1 for d in dg if d == "Đúng hạn")
        kq = [po_ket_qua_cl(p) for p in ncc_pos]
        kiem = sum(1 for k in kq if k in ("Đạt", "Không đạt"))
        dat = sum(1 for k in kq if k == "Đạt")
        con = sum(cong_no_theo_po(p, thanh_toans, ncc_index, today)["con_phai_tra"]
                  for p in ncc_pos)
        rows.append({
            "ma_ncc": ncc.ma_ncc, "ten": ncc.ten, "danh_gia": ncc.danh_gia,
            "so_bao_gia": len(bg), "so_trung_thau": so_chon,
            "ty_le_trung_thau": so_chon / len(bg) if bg else 0,
            "so_po": len(ncc_pos), "gia_tri_mua": gia_tri_mua,
            "ty_le_giao_dung_han": dung_han / den_han if den_han else 0,
            "ty_le_dat_cl": dat / kiem if kiem else 0,
            "con_phai_tra": con,
        })
    rows.sort(key=lambda r: r["gia_tri_mua"], reverse=True)
    return rows


# ---- Thống kê dự án ------------------------------------------------------

def thong_ke_du_an(du_ans, check_gias, prs, pos) -> list[dict]:
    cg_index = _index(check_gias, "ma_yc")
    pr_index = _index(prs, "ma_pr")
    yc_du_an = {c.ma_yc: c.ma_du_an for c in check_gias}
    pr_du_an = {p.ma_pr: yc_du_an.get(p.ma_yc, "") for p in prs}
    rows = []
    for da in du_ans:
        yc = [c for c in check_gias if c.ma_du_an == da.ma_du_an]
        pr = [p for p in prs if pr_du_an.get(p.ma_pr) == da.ma_du_an]
        po = [p for p in pos if du_an_cua_po(p, pr_index, cg_index) == da.ma_du_an]
        gia_tri_po = sum(po_gia_tri(p) for p in po)
        tiet_kiem = sum(po_tiet_kiem(p, pr_index) for p in po)
        rows.append({
            "ma_du_an": da.ma_du_an, "ten": da.ten, "trang_thai": da.trang_thai,
            "ngan_sach": da.ngan_sach or 0,
            "so_yc": len(yc), "tong_du_toan_yc": sum(cg_gia_tri_du_toan(c) for c in yc),
            "so_pr": len(pr), "so_po": len(po), "gia_tri_po": gia_tri_po,
            "tiet_kiem": tiet_kiem,
            "ty_le_su_dung": gia_tri_po / (da.ngan_sach or 0) if (da.ngan_sach or 0) else 0,
            "con_lai": (da.ngan_sach or 0) - gia_tri_po,
        })
    return rows


# ---- Báo cáo tháng (12 tháng của 1 năm) ---------------------------------

def bao_cao_thang(check_gias, prs, pos, thanh_toans) -> list[dict]:
    """12 dòng tháng. Dữ liệu truyền vào nên đã lọc theo năm cần xem."""
    pr_index = _index(prs, "ma_pr")
    rows = []
    for m in range(1, 13):
        po_m = [p for p in pos if p.ngay and p.ngay.month == m]
        rows.append({
            "thang": m,
            "so_yc": sum(1 for c in check_gias if c.ngay_nhan and c.ngay_nhan.month == m),
            "so_pr": sum(1 for p in prs if p.ngay and p.ngay.month == m),
            "so_po": len(po_m),
            "gia_tri_po": sum(po_gia_tri(p) for p in po_m),
            "tien_chi": sum(t.so_tien or 0 for t in thanh_toans
                            if t.ngay and t.ngay.month == m),
            "tiet_kiem": sum(po_tiet_kiem(p, pr_index) for p in po_m),
        })
    return rows
