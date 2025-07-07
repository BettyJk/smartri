@echo off
REM Clean up unnecessary files and folders for Streamlit version
if exist "main.py" del "main.py"
if exist "start_backend.bat" del "start_backend.bat"
if exist "README_DEPLOY.md" del "README_DEPLOY.md"
if exist "frontend" rmdir /s /q "frontend"
