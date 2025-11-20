@echo off
echo ========================================
echo ChatGPT to Evernote - Build Script
echo ========================================
echo.

echo [1/3] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo Done.
echo.

echo [2/3] Building executable with PyInstaller...
pyinstaller evernote_server.spec --clean
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)
echo Done.
echo.

echo [3/3] Creating distribution package...
if not exist dist\ChatGPT_to_Evernote mkdir dist\ChatGPT_to_Evernote
move dist\ChatGPT_to_Evernote.exe dist\ChatGPT_to_Evernote\ >nul
xcopy chrome-extension dist\ChatGPT_to_Evernote\chrome-extension\ /E /I /Y >nul
copy .env.example dist\ChatGPT_to_Evernote\.env.example >nul
copy README.md dist\ChatGPT_to_Evernote\ >nul
echo Done.
echo.

echo ========================================
echo Build completed successfully!
echo.
echo Output: dist\ChatGPT_to_Evernote\
echo   - ChatGPT_to_Evernote.exe
echo   - chrome-extension\
echo   - .env.example
echo   - README.md
echo ========================================
pause
