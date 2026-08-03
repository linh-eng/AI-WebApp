"""Tạo PDF Đơn đặt hàng / Hợp đồng mua (PO) — hỗ trợ tiếng Việt bằng font DejaVuSans."""
from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .config import BASE_DIR, COMPANY_INFO, COMPANY_NAME

_FONT_DIR = BASE_DIR / "app" / "static" / "fonts"
_REGISTERED = False


def _dang_ky_font():
    global _REGISTERED
    if _REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("DejaVu", str(_FONT_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(_FONT_DIR / "DejaVuSans-Bold.ttf")))
    _REGISTERED = True


def _tien(v) -> str:
    return f"{float(v or 0):,.0f}".replace(",", ".")


def _ngay(d) -> str:
    return d.strftime("%d/%m/%Y") if d else ""


def xuat_pdf_po(po, ncc, tt: dict) -> bytes:
    """Trả về nội dung PDF (bytes) cho một PO/hợp đồng.

    `tt` gồm: hang_muc, dvt, ten_du_an, dieu_khoan_tt, han_thanh_toan.
    """
    _dang_ky_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm,
                            bottomMargin=16 * mm, leftMargin=16 * mm, rightMargin=16 * mm)

    p_small = ParagraphStyle("s", fontName="DejaVu", fontSize=8.5, leading=12,
                             textColor=colors.HexColor("#555555"))
    p_h1 = ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=18, leading=22,
                          textColor=colors.HexColor("#0d5ba5"))
    p_company = ParagraphStyle("c", fontName="DejaVu-Bold", fontSize=13, leading=16)
    p_right = ParagraphStyle("r", fontName="DejaVu", fontSize=9, leading=12, alignment=2)
    p_cell = ParagraphStyle("cell", fontName="DejaVu", fontSize=9, leading=12)
    p_cellb = ParagraphStyle("cellb", fontName="DejaVu-Bold", fontSize=9, leading=12)
    p_center = ParagraphStyle("ct", fontName="DejaVu", fontSize=9, leading=12, alignment=1)
    p_centerb = ParagraphStyle("ctb", fontName="DejaVu-Bold", fontSize=10, leading=13, alignment=1)

    el = []
    el.append(Paragraph(COMPANY_NAME, p_company))
    el.append(Paragraph(COMPANY_INFO, p_small))
    el.append(Spacer(1, 7 * mm))
    el.append(Paragraph("ĐƠN ĐẶT HÀNG / HỢP ĐỒNG MUA", p_h1))
    if po.so_hop_dong:
        el.append(Paragraph(f"Số hợp đồng: {po.so_hop_dong}", p_small))
    el.append(Spacer(1, 4 * mm))

    # Thông tin PO & NCC (2 cột)
    ten_ncc = ncc.ten if ncc else po.ma_ncc
    lien_he = ""
    if ncc:
        lien_he = " · ".join(filter(None, [ncc.nguoi_lien_he, ncc.dien_thoai, ncc.email]))
    info = [
        [Paragraph(f"<b>Số PO:</b> {po.ma_po}", p_cell),
         Paragraph(f"<b>Ngày PO:</b> {_ngay(po.ngay)}", p_cell)],
        [Paragraph(f"<b>Dự án:</b> {tt.get('ten_du_an', '')}", p_cell),
         Paragraph(f"<b>Ngày ký HĐ:</b> {_ngay(po.ngay_ky)}", p_cell)],
        [Paragraph(f"<b>Nhà cung cấp:</b> {ten_ncc}", p_cell),
         Paragraph(f"<b>MST:</b> {ncc.ma_so_thue if ncc else ''}", p_cell)],
        [Paragraph(f"<b>Liên hệ:</b> {lien_he}", p_cell),
         Paragraph(f"<b>Địa chỉ:</b> {ncc.dia_chi if ncc else ''}", p_cell)],
    ]
    t_info = Table(info, colWidths=[100 * mm, 78 * mm])
    t_info.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    el.append(t_info)
    el.append(Spacer(1, 5 * mm))

    # Bảng hàng hoá (1 dòng)
    so_luong = po.so_luong_dat or 0
    don_gia = po.don_gia_po or 0
    thanh_tien = so_luong * don_gia
    header = ["STT", "Hạng mục / Tên hàng", "ĐVT", "SL đặt", "Đơn giá", "Thành tiền"]
    data = [[Paragraph(f"<b>{h}</b>", p_cellb) for h in header]]
    data.append([
        Paragraph("1", p_cell), Paragraph(tt.get("hang_muc", ""), p_cell),
        Paragraph(tt.get("dvt", ""), p_cell), Paragraph(_tien(so_luong), p_right),
        Paragraph(_tien(don_gia), p_right), Paragraph(_tien(thanh_tien), p_right),
    ])
    # Dòng tổng
    p_lblb = ParagraphStyle("lblb", fontName="DejaVu-Bold", fontSize=10, leading=13, alignment=2)
    p_rb = ParagraphStyle("rb", parent=p_right, fontName="DejaVu-Bold", fontSize=10)
    data.append(["", Paragraph("TỔNG GIÁ TRỊ PO:", p_lblb), "", "", "",
                 Paragraph(_tien(thanh_tien), p_rb)])

    col_w = [12 * mm, 74 * mm, 16 * mm, 20 * mm, 28 * mm, 28 * mm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    n = len(data)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f9")),
        ("GRID", (0, 0), (-1, n - 2), 0.5, colors.HexColor("#c9d4e3")),
        ("LINEABOVE", (4, n - 1), (-1, n - 1), 1, colors.HexColor("#0d5ba5")),
        ("SPAN", (1, n - 1), (4, n - 1)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    el.append(t)
    el.append(Spacer(1, 5 * mm))

    # Điều khoản giao hàng & thanh toán
    dk = [
        [Paragraph(f"<b>Ngày giao cam kết:</b> {_ngay(po.ngay_giao_cam_ket)}", p_cell),
         Paragraph(f"<b>Điều khoản TT:</b> {tt.get('dieu_khoan_tt', 0)} ngày", p_cell)],
        [Paragraph(f"<b>Hạn thanh toán:</b> {_ngay(tt.get('han_thanh_toan'))}", p_cell),
         Paragraph(f"<b>Ghi chú:</b> {po.ghi_chu or ''}", p_cell)],
    ]
    t_dk = Table(dk, colWidths=[100 * mm, 78 * mm])
    t_dk.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    el.append(t_dk)
    el.append(Spacer(1, 12 * mm))

    # Ô ký tên hai bên
    ky = [
        [Paragraph("ĐẠI DIỆN BÊN MUA", p_centerb), Paragraph("ĐẠI DIỆN BÊN BÁN", p_centerb)],
        [Paragraph(COMPANY_NAME, p_center), Paragraph(ten_ncc, p_center)],
        [Paragraph("(Ký, ghi rõ họ tên)", p_small), Paragraph("(Ký, ghi rõ họ tên)", p_small)],
    ]
    t_ky = Table(ky, colWidths=[89 * mm, 89 * mm])
    t_ky.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 1), (-1, 1), 22),
    ]))
    el.append(t_ky)

    doc.build(el)
    return buf.getvalue()
