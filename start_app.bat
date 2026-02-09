@echo off
echo ============================================
echo   ADS ESTIMATION HUB - STREAMLIT APP
echo ============================================
echo.
echo Pokrecem aplikaciju...
echo.

cd /d "%~dp0"
python -m streamlit run hub_app.py
pause
