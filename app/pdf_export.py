"""Tạo PDF báo giá (hỗ trợ tiếng Việt bằng font DejaVuSans nhúng sẵn)."""
from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from reportlab.lib.styles import ParagraphStyle

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


def xuat_pdf_bao_gia(bg, khach, dong_list) -> bytes:
    """Trả về nội dung PDF (bytes) cho một báo giá."""
    _dang_ky_font()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=18 * mm,
                            bottomMargin=18 * mm, leftMargin=16 * mm, rightMargin=16 * mm)

    p_normal = ParagraphStyle("n", fontName="DejaVu", fontSize=10, leading=14)
    p_small = ParagraphStyle("s", fontName="DejaVu", fontSize=8.5, leading=12,
                             textColor=colors.HexColor("#555555"))
    p_h1 = ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=18, leading=22,
                          textColor=colors.HexColor("#0d5ba5"))
    p_company = ParagraphStyle("c", fontName="DejaVu-Bold", fontSize=13, leading=16)
    p_right = ParagraphStyle("r", fontName="DejaVu", fontSize=10, leading=14,
                             alignment=2)
    p_cell = ParagraphStyle("cell", fontName="DejaVu", fontSize=9, leading=12)
    p_cellb = ParagraphStyle("cellb", fontName="DejaVu-Bold", fontSize=9, leading=12)

    el = []
    el.append(Paragraph(COMPANY_NAME, p_company))
    el.append(Paragraph(COMPANY_INFO, p_small))
    el.append(Spacer(1, 8 * mm))
    el.append(Paragraph("BÁO GIÁ", p_h1))
    el.append(Spacer(1, 4 * mm))

    # Thông tin báo giá & khách hàng (2 cột)
    ten_kh = khach.ten if khach else bg.ma_kh
    lien_he = ""
    if khach:
        lien_he = " · ".join(filter(None, [khach.nguoi_lien_he, khach.lien_he]))
    info = [
        [Paragraph(f"<b>Số báo giá:</b> {bg.ma_bao_gia}", p_cell),
         Paragraph(f"<b>Ngày:</b> {_ngay(bg.ngay)}", p_cell)],
        [Paragraph(f"<b>Khách hàng:</b> {ten_kh}", p_cell),
         Paragraph(f"<b>Hiệu lực đến:</b> {_ngay(bg.hieu_luc_den)}", p_cell)],
        [Paragraph(f"<b>Liên hệ:</b> {lien_he}", p_cell),
         Paragraph(f"<b>NV phụ trách:</b> {bg.nv_phu_trach or ''}", p_cell)],
    ]
    t_info = Table(info, colWidths=[95 * mm, 83 * mm])
    t_info.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    el.append(t_info)
    el.append(Spacer(1, 5 * mm))

    # Bảng dòng hàng
    header = ["STT", "Nội dung / Tên hàng", "ĐVT", "SL", "Đơn giá", "Thành tiền"]
    data = [[Paragraph(f"<b>{h}</b>", p_cellb) for h in header]]
    tong_truoc_vat = 0.0
    if dong_list:
        for i, d in enumerate(dong_list, 1):
            tt = (d.so_luong or 0) * (d.don_gia or 0)
            tong_truoc_vat += tt
            data.append([
                Paragraph(str(i), p_cell),
                Paragraph(d.ten_hang or d.ma_sp, p_cell),
                Paragraph(d.don_vi or "", p_cell),
                Paragraph(_tien(d.so_luong), p_right),
                Paragraph(_tien(d.don_gia), p_right),
                Paragraph(_tien(tt), p_right),
            ])
    else:
        # Không có dòng chi tiết -> dùng nội dung & giá trị tổng của báo giá
        tong_truoc_vat = bg.gia_truoc_vat or 0
        data.append([
            Paragraph("1", p_cell), Paragraph(bg.noi_dung or "", p_cell),
            Paragraph("", p_cell), Paragraph("", p_right), Paragraph("", p_right),
            Paragraph(_tien(tong_truoc_vat), p_right),
        ])

    vat = bg.vat or 0
    tien_vat = tong_truoc_vat * vat
    tong_sau_vat = tong_truoc_vat + tien_vat

    p_lbl = ParagraphStyle("lbl", fontName="DejaVu", fontSize=9, leading=12, alignment=2)
    p_lblb = ParagraphStyle("lblb", fontName="DejaVu-Bold", fontSize=10, leading=13, alignment=2)
    p_rb = ParagraphStyle("rb", parent=p_right, fontName="DejaVu-Bold", fontSize=10)

    def _tong_row(nhan, gia_tri, bold=False):
        return ["", Paragraph(nhan, p_lblb if bold else p_lbl), "", "", "",
                Paragraph(_tien(gia_tri), p_rb if bold else p_right)]

    data.append(_tong_row("Cộng trước VAT:", tong_truoc_vat))
    data.append(_tong_row(f"VAT ({vat*100:.0f}%):", tien_vat))
    data.append(_tong_row("TỔNG THANH TOÁN:", tong_sau_vat, bold=True))

    col_w = [12 * mm, 74 * mm, 16 * mm, 18 * mm, 28 * mm, 30 * mm]
    t = Table(data, colWidths=col_w, repeatRows=1)
    n_dong = len(data)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "DejaVu"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f9")),
        ("GRID", (0, 0), (-1, n_dong - 4), 0.5, colors.HexColor("#c9d4e3")),
        ("LINEABOVE", (4, n_dong - 3), (-1, n_dong - 3), 0.5, colors.HexColor("#c9d4e3")),
        ("LINEABOVE", (4, n_dong - 1), (-1, n_dong - 1), 1, colors.HexColor("#0d5ba5")),
        ("SPAN", (1, n_dong - 3), (4, n_dong - 3)),
        ("SPAN", (1, n_dong - 2), (4, n_dong - 2)),
        ("SPAN", (1, n_dong - 1), (4, n_dong - 1)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    el.append(t)
    el.append(Spacer(1, 8 * mm))
    el.append(Paragraph("Trân trọng cảm ơn Quý khách. Báo giá có hiệu lực đến ngày "
                        f"{_ngay(bg.hieu_luc_den)}.", p_small))

    doc.build(el)
    return buf.getvalue()
