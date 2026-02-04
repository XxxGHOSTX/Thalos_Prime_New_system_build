@echo off
REM THALOS Prime GUI Launcher (Windows)
REM Double-click this file to launch the GUI

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║               THALOS PRIME v3.2.0 GUI Launcher            ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Starting THALOS Prime GUI Application...
echo.

python thalos_prime_gui.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to launch GUI
    echo Please ensure Python is installed and all dependencies are met
    echo.
    pause
)
