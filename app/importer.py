"""Nhập nhanh dữ liệu từ file Excel (.xlsx) hoặc CSV.

Cách dùng: người dùng tải file mẫu (nút "Tải file mẫu" trên mỗi màn hình), điền
nhiều dòng rồi upload. Hệ thống tự dò dòng tiêu đề (khớp theo nhãn cột hoặc tên
trường), đọc dữ liệu và thêm/cập nhật theo mã (khoá chính).
"""
from __future__ import annotations

import csv
import io
from datetime import date, datetime


def _parse_number(s: str) -> float:
    s = str(s).strip().replace(" ", "")
    if s == "":
        return 0.0
    # Hỗ trợ định dạng VN: dấu . ngăn cách nghìn, , là thập phân
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0


def _parse_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    if s == "":
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def coerce(field: dict, value):
    """Chuyển giá trị ô (đã có kiểu hoặc chuỗi) về đúng kiểu của trường."""
    t = field["type"]
    if value is None:
        return 0 if t in ("money", "number", "percent") else (None if t == "date" else "")
    if t in ("money", "number"):
        return float(value) if isinstance(value, (int, float)) else _parse_number(value)
    if t == "percent":
        if isinstance(value, (int, float)):
            v = float(value)
        else:
            v = _parse_number(str(value).replace("%", ""))
        # Chấp nhận cả "8" (8%) lẫn "0.08" (dạng phân số)
        return v if v <= 1 else v / 100.0
    if t == "date":
        return _parse_date(value)
    return str(value).strip()


def _rows_from_bytes(filename: str, content: bytes) -> list[list]:
    """Trả về danh sách các dòng (mỗi dòng là list ô) từ file .xlsx hoặc .csv."""
    if filename.lower().endswith(".csv"):
        text = content.decode("utf-8-sig", errors="replace")
        return [list(r) for r in csv.reader(io.StringIO(text))]
    # .xlsx / .xlsm
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    ws = wb.active
    return [list(r) for r in ws.iter_rows(values_only=True)]


def _norm(s) -> str:
    return str(s).strip().lower() if s is not None else ""


def doc_du_lieu(filename: str, content: bytes, fields: list[dict]):
    """Đọc file -> danh sách bản ghi (dict tên_trường -> giá trị thô).

    Tự dò dòng tiêu đề trong 8 dòng đầu (khớp nhiều nhất với nhãn/tên trường).
    """
    all_rows = _rows_from_bytes(filename, content)
    if not all_rows:
        return [], "File rỗng."

    label2name = {_norm(f["label"]): f["name"] for f in fields}
    name2name = {_norm(f["name"]): f["name"] for f in fields}

    # Tìm dòng tiêu đề: dòng có nhiều ô khớp nhãn/tên trường nhất.
    best_idx, best_map, best_hits = None, {}, 0
    for idx, row in enumerate(all_rows[:8]):
        colmap, hits = {}, 0
        for i, cell in enumerate(row):
            key = _norm(cell)
            if key in label2name:
                colmap[i] = label2name[key]; hits += 1
            elif key in name2name:
                colmap[i] = name2name[key]; hits += 1
        if hits > best_hits:
            best_idx, best_map, best_hits = idx, colmap, hits

    if best_idx is None or best_hits == 0:
        return [], "Không nhận diện được cột nào khớp với mẫu. Hãy dùng đúng file mẫu tải từ hệ thống."

    records = []
    for row in all_rows[best_idx + 1:]:
        if all(c is None or str(c).strip() == "" for c in row):
            continue
        rec = {}
        for i, name in best_map.items():
            rec[name] = row[i] if i < len(row) else None
        records.append(rec)
    return records, None


def tao_file_mau(fields: list[dict], pk: str) -> bytes:
    """Tạo file CSV mẫu: dòng tiêu đề (nhãn cột) + 1 dòng ví dụ để người dùng điền."""
    vi_du = {
        "text": "Ví dụ", "number": "0", "money": "1000000",
        "percent": "8", "date": "2026-01-31", "select": "",
    }
    headers = [f["label"] for f in fields]
    example = [("MÃ_VÍ_DỤ" if f["name"] == pk else vi_du.get(f["type"], "")) for f in fields]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerow(example)
    return buf.getvalue().encode("utf-8-sig")
