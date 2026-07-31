"""Xuất báo cáo Excel: điền dữ liệu từ CSDL vào file mẫu THNG.

Nguyên tắc giữ nguyên định dạng: KHÔNG vẽ lại Excel. Ta mở chính file mẫu, chỉ
ghi giá trị vào các Ô NHẬP TAY (cột chữ xanh) theo đúng vị trí; mọi công thức
(tên KH, giá sau VAT, công nợ, tiến độ...) đã có sẵn trong file mẫu và sẽ tự
tính lại khi mở bằng Excel (đặt fullCalcOnLoad=True để buộc tính lại).
"""
from __future__ import annotations

import io

import openpyxl

from . import models
from .config import TEMPLATE_XLSX

DATA_START_ROW = 4

# Ánh xạ (thuộc tính model -> chỉ số cột). CHỈ liệt kê ô nhập tay; bỏ qua cột
# công thức để không ghi đè công thức trong file mẫu.
COT_KHACH_HANG = {
    "ma_kh": 1, "ten": 2, "nguoi_lien_he": 3, "lien_he": 4,
    "dieu_khoan_tt": 5, "han_muc_cong_no": 6, "ghi_chu": 7,
}
COT_BAO_GIA = {
    "ma_bao_gia": 1, "ngay": 2, "ma_kh": 3, "noi_dung": 5, "gia_truoc_vat": 6,
    "vat": 7, "hieu_luc_den": 9, "trang_thai": 10, "ma_po": 11,
    "nv_phu_trach": 12, "ghi_chu": 15,
}
COT_HOP_DONG = {
    "ma_po": 1, "ngay_nhan_po": 2, "ma_bao_gia": 3, "so_hop_dong": 6,
    "ngay_ky": 7, "gia_tri_hop_dong": 8, "ngay_giao_cam_ket": 10,
    "ngay_giao_thuc_te": 11, "tinh_trang_chat_luong": 14, "ty_le_hang_loi": 15,
    "ghi_chu": 19,
}
COT_THANH_TOAN = {
    "ma_phieu_thu": 1, "ngay_thu": 2, "ma_po": 3, "so_tien_thu": 5,
    "hinh_thuc": 6, "dot_noi_dung": 7,
}

# Số dòng dữ liệu tối đa mỗi sheet (theo vùng công thức có sẵn trong file mẫu).
MAX_ROWS = {
    "Khách hàng": 100,
    "Báo giá": 200,
    "Hợp đồng": 200,
    "Thanh toán": 300,
}


def _ghi_sheet(ws, records, colmap, max_rows):
    """Xoá dữ liệu ví dụ ở các ô nhập tay rồi ghi records vào."""
    last_row = DATA_START_ROW + max_rows - 1
    # Xoá giá trị cũ ở các ô nhập tay (giữ nguyên công thức & định dạng).
    for r in range(DATA_START_ROW, last_row + 1):
        for col in colmap.values():
            ws.cell(row=r, column=col).value = None
    # Ghi dữ liệu thật.
    for i, rec in enumerate(records[:max_rows]):
        r = DATA_START_ROW + i
        for attr, col in colmap.items():
            ws.cell(row=r, column=col).value = getattr(rec, attr)


def xuat_bao_cao(
    khachs: list[models.KhachHang],
    bao_gias: list[models.BaoGia],
    hop_dongs: list[models.HopDong],
    thanh_toans: list[models.ThanhToan],
) -> bytes:
    """Trả về nội dung file .xlsx (bytes) đã điền dữ liệu, đúng mẫu THNG."""
    if not TEMPLATE_XLSX.exists():
        raise FileNotFoundError(f"Không tìm thấy file mẫu: {TEMPLATE_XLSX}")

    wb = openpyxl.load_workbook(TEMPLATE_XLSX)

    _ghi_sheet(wb["Khách hàng"], khachs, COT_KHACH_HANG, MAX_ROWS["Khách hàng"])
    _ghi_sheet(wb["Báo giá"], bao_gias, COT_BAO_GIA, MAX_ROWS["Báo giá"])
    _ghi_sheet(wb["Hợp đồng"], hop_dongs, COT_HOP_DONG, MAX_ROWS["Hợp đồng"])
    _ghi_sheet(wb["Thanh toán"], thanh_toans, COT_THANH_TOAN, MAX_ROWS["Thanh toán"])

    # Buộc Excel tính lại toàn bộ công thức khi mở file.
    wb.calculation.fullCalcOnLoad = True

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()
