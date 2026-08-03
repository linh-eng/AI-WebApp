@echo off
REM ===== Chay WebApp Bao cao MUA HANG THNG tren Windows (cong 8010) =====
REM Dung cong 8010 de chay SONG SONG voi app khac dang o cong 8000.
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
echo   WebApp MUA HANG - Mo trinh duyet vao:  http://127.0.0.1:8010
echo   Dang nhap:  admin  /  admin123
echo   De TAT ung dung: dong cua so nay hoac bam Ctrl + C
echo ================================================================
echo.
start "" http://127.0.0.1:8010
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
pause
