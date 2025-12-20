@echo off
echo ========================================
echo   Minmatar Rebellion - EXE Builder
echo ========================================
echo.

echo [1/4] Installing PyInstaller...
pip install pyinstaller

echo.
echo [2/4] Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "MinmatarRebellion" ^
    --icon=icon.ico ^
    --add-data "svg;svg" ^
    --add-data "data;data" ^
    --add-data "README.md;." ^
    main.py

echo.
echo [3/4] Copying additional files...
xcopy /E /I svg dist\svg
xcopy /E /I data dist\data
copy README.md dist\
copy QUICKSTART.md dist\

echo.
echo [4/4] Build complete!
echo.
echo ========================================
echo   EXE Location: dist\MinmatarRebellion.exe
echo ========================================
echo.
echo You can now distribute the 'dist' folder!
echo.
pause
