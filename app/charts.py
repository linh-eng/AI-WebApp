"""Vẽ biểu đồ bằng SVG server-side (không cần thư viện/CDN, chạy offline).

Màu lấy từ bảng màu đã kiểm định (đạt CVD/độ tương phản): xanh #2a78d6, cam #eb6834.
Biểu đồ công nợ dùng thang màu trạng thái theo mức độ quá hạn, có nhãn trực tiếp
nên không phụ thuộc vào màu để phân biệt.
"""
from __future__ import annotations

from html import escape

SERIES1 = "#2a78d6"   # Giá trị HĐ ký
SERIES2 = "#eb6834"   # Tiền thu
INK = "#1f2937"
INK2 = "#6b7280"
GRID = "#e5e9f0"

MAU_TUOI_NO = {
    "Trong hạn": "#1baf7a",
    "Quá hạn 1-30 ngày": "#eda100",
    "Quá hạn 31-60 ngày": "#eb6834",
    "Quá hạn 61-90 ngày": "#e34948",
    "Quá hạn trên 90 ngày": "#991b1b",
}


def rut_gon_tien(v) -> str:
    v = float(v or 0)
    if v >= 1e9:
        return f"{v / 1e9:.2f} tỷ".replace(".", ",")
    if v >= 1e6:
        return f"{v / 1e6:.0f} tr"
    if v >= 1e3:
        return f"{v / 1e3:.0f} k"
    return f"{v:.0f}"


def _tien_day_du(v) -> str:
    return f"{float(v or 0):,.0f}".replace(",", ".") + " ₫"


def bieu_do_thang(dien_bien: list[dict]) -> str:
    """Biểu đồ cột nhóm: Giá trị HĐ ký & Tiền thu theo 12 tháng."""
    W, H = 760, 300
    pad_l, pad_r, pad_t, pad_b = 54, 12, 28, 34
    plot_w = W - pad_l - pad_r
    plot_h = H - pad_t - pad_b
    vmax = max([max(d["gt_hd_ky"], d["tien_thu"]) for d in dien_bien] + [1])

    def y(v):
        return pad_t + plot_h * (1 - v / vmax)

    parts = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
             f'style="max-width:100%;height:auto" font-family="Arial,sans-serif">']

    # Lưới ngang + nhãn trục y (4 mốc)
    for i in range(5):
        val = vmax * i / 4
        yy = y(val)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{W-pad_r}" y2="{yy:.1f}" '
                     f'stroke="{GRID}" stroke-width="1"/>')
        parts.append(f'<text x="{pad_l-6}" y="{yy+3:.1f}" text-anchor="end" '
                     f'font-size="10" fill="{INK2}">{escape(rut_gon_tien(val))}</text>')

    n = len(dien_bien)
    group_w = plot_w / n
    bw = min(14, group_w / 2.6)
    gap = 2
    for i, d in enumerate(dien_bien):
        gx = pad_l + group_w * i + group_w / 2
        x1 = gx - bw - gap / 2
        x2 = gx + gap / 2
        for x, val, color, ten in (
            (x1, d["gt_hd_ky"], SERIES1, "Giá trị PO"),
            (x2, d["tien_thu"], SERIES2, "Tiền chi NCC"),
        ):
            h = plot_h * (val / vmax)
            yy = pad_t + plot_h - h
            if h > 0:
                parts.append(
                    f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{h:.1f}" '
                    f'rx="3" fill="{color}"><title>Tháng {d["thang"]} · {ten}: '
                    f'{escape(_tien_day_du(val))}</title></rect>')
        parts.append(f'<text x="{gx:.1f}" y="{H-pad_b+16}" text-anchor="middle" '
                     f'font-size="10" fill="{INK2}">T{d["thang"]}</text>')

    # Chú giải
    lx, ly = pad_l, 14
    parts.append(f'<rect x="{lx}" y="{ly-9}" width="11" height="11" rx="2" fill="{SERIES1}"/>')
    parts.append(f'<text x="{lx+16}" y="{ly}" font-size="11" fill="{INK}">Giá trị PO</text>')
    parts.append(f'<rect x="{lx+110}" y="{ly-9}" width="11" height="11" rx="2" fill="{SERIES2}"/>')
    parts.append(f'<text x="{lx+126}" y="{ly}" font-size="11" fill="{INK}">Tiền chi NCC</text>')

    parts.append("</svg>")
    return "".join(parts)


def bieu_do_tuoi_no(buckets: list[dict]) -> str:
    """Biểu đồ thanh ngang: còn phải thu theo nhóm tuổi nợ, có nhãn trực tiếp."""
    rows = [b for b in buckets]
    vmax = max([b["so_tien"] for b in rows] + [1])
    W = 760
    row_h = 34
    pad_l, pad_r, pad_t = 150, 90, 8
    H = pad_t + row_h * len(rows) + 8
    plot_w = W - pad_l - pad_r

    parts = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" '
             f'style="max-width:100%;height:auto" font-family="Arial,sans-serif">']
    for i, b in enumerate(rows):
        cy = pad_t + row_h * i
        color = MAU_TUOI_NO.get(b["nhom"], SERIES1)
        bw = plot_w * (b["so_tien"] / vmax)
        parts.append(f'<text x="{pad_l-8}" y="{cy+row_h/2+4:.1f}" text-anchor="end" '
                     f'font-size="11" fill="{INK}">{escape(b["nhom"])}</text>')
        parts.append(f'<rect x="{pad_l}" y="{cy+6:.1f}" width="{max(bw,2):.1f}" '
                     f'height="{row_h-14}" rx="3" fill="{color}">'
                     f'<title>{escape(b["nhom"])}: {escape(_tien_day_du(b["so_tien"]))}</title></rect>')
        parts.append(f'<text x="{pad_l+max(bw,2)+6:.1f}" y="{cy+row_h/2+4:.1f}" '
                     f'font-size="10" fill="{INK2}">{escape(rut_gon_tien(b["so_tien"]))}</text>')
    parts.append("</svg>")
    return "".join(parts)


def bieu_do_vong(ty_le: float, nhan: str) -> str:
    """Vòng tròn tỷ lệ (donut) cho tỷ lệ thắng thầu / giao đúng hạn."""
    import math

    W = H = 150
    cx = cy = 75
    r = 56
    sw = 16
    pct = max(0.0, min(1.0, ty_le or 0))
    circ = 2 * math.pi * r
    dash = circ * pct
    parts = [f'<svg viewBox="0 0 {W} {H}" width="150" role="img" font-family="Arial,sans-serif">']
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{GRID}" stroke-width="{sw}"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SERIES1}" '
                 f'stroke-width="{sw}" stroke-linecap="round" '
                 f'stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')
    parts.append(f'<text x="{cx}" y="{cy-2}" text-anchor="middle" font-size="26" '
                 f'font-weight="700" fill="{INK}">{pct*100:.0f}%</text>')
    parts.append(f'<text x="{cx}" y="{cy+18}" text-anchor="middle" font-size="10" '
                 f'fill="{INK2}">{escape(nhan)}</text>')
    parts.append("</svg>")
    return "".join(parts)
