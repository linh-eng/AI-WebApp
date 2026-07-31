@echo off
REM ===== Chay WebApp cho CA PHONG truy cap qua mang noi bo (LAN) =====
REM Chay file nay tren MOT may lam "may chu". Dong nghiep mo trinh duyet vao
REM dia chi IPv4 cua may nay (vd http://192.168.1.50:8000).
cd /d "%~dp0"

where py >nul 2>nul && (set PY=py) || (set PY=python)
if not exist ".venv" (
  echo Dang tao moi truong lan dau...
  %PY% -m venv .venv
)
call ".venv\Scripts\activate"
echo Dang cai dat / kiem tra thu vien...
python -m pip install --disable-pip-version-check -q -r requirements.txt

echo.
echo ==========================================================
echo   DIA CHI DE DONG NGHIEP TRUY CAP:
echo.
echo   CACH 1 - Bang ten may (de nho, on dinh nhat):
echo       http://%COMPUTERNAME%:8000
echo.
echo   CACH 2 - Bang dia chi IPv4 (chon dong 192.168... hoac 10...):
ipconfig | findstr /C:"IPv4"
echo       http://[DIA-CHI-IPv4]:8000
echo.
echo   Tren chinh may nay:          http://127.0.0.1:8000
echo   Dang nhap admin / admin123  (nho doi mat khau ngay)
echo.
echo   * Lan dau Windows co the hoi "Allow access" -> bam Allow.
echo   * De TAT: dong cua so nay. GIU may bat de moi nguoi dung duoc.
echo ==========================================================
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
