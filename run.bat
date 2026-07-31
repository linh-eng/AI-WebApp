@echo off
REM ===== Chay WebApp Bao cao Kinh doanh THNG tren Windows =====
REM Bam doi (double-click) file nay de chay. Lan dau se cai dat, hoi lau mot chut.
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
echo ================================================================
echo   Mo trinh duyet vao dia chi:  http://127.0.0.1:8000
echo   Dang nhap:  admin  /  admin123
echo   De TAT ung dung: dong cua so nay hoac bam Ctrl + C
echo ================================================================
echo.
start "" http://127.0.0.1:8000
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
