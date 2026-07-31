FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY docs/templates ./docs/templates

# Thư mục lưu CSDL SQLite (nên gắn volume khi chạy thật)
RUN mkdir -p /app/data
ENV DATA_DIR=/app/data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
