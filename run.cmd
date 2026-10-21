@echo off
setlocal
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Project Python environment not found. Follow the setup instructions in README.md.
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0main.py" %*
exit /b %errorlevel%
