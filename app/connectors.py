"""Kết nối & đồng bộ dữ liệu từ nguồn ngoài (Giai đoạn 3).

Hỗ trợ lấy dữ liệu từ một URL trả về CSV hoặc JSON — ví dụ:
- Google Sheets "Publish to web" ở dạng CSV.
- Endpoint xuất dữ liệu của phần mềm bán hàng/kế toán/ERP công ty (CSV hoặc JSON).

Trả về danh sách bản ghi (dict tên_trường -> giá trị thô) để tầng trên upsert.
"""
from __future__ import annotations

import json
import urllib.request

from . import importer


def _tai_url(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "THNG-Report/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _norm(s) -> str:
    return str(s).strip().lower() if s is not None else ""


def _records_tu_json(content: bytes, fields: list[dict]):
    try:
        data = json.loads(content.decode("utf-8", errors="replace"))
    except Exception as e:
        return [], f"JSON không hợp lệ: {e}"
    if isinstance(data, dict):
        # Chấp nhận {"data": [...]} hoặc lấy danh sách đầu tiên tìm được
        rows = data.get("data")
        if rows is None:
            rows = next((v for v in data.values() if isinstance(v, list)), None)
    else:
        rows = data
    if not isinstance(rows, list):
        return [], "JSON không chứa danh sách bản ghi."

    label2name = {_norm(f["label"]): f["name"] for f in fields}
    name2name = {_norm(f["name"]): f["name"] for f in fields}
    records = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        rec = {}
        for k, v in row.items():
            key = _norm(k)
            name = name2name.get(key) or label2name.get(key)
            if name:
                rec[name] = v
        if rec:
            records.append(rec)
    return records, None


def doc_tu_url(url: str, dinh_dang: str, fields: list[dict]):
    """Tải & đọc dữ liệu từ URL. Trả về (records, loi)."""
    url = (url or "").strip()
    if not url:
        return [], "Chưa cấu hình URL."
    try:
        content = _tai_url(url)
    except Exception as e:
        return [], f"Không tải được URL: {e}"
    if dinh_dang == "json":
        return _records_tu_json(content, fields)
    # CSV: tái dùng bộ đọc của importer
    return importer.doc_du_lieu("nguon.csv", content, fields)
