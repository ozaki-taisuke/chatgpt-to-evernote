@echo off
REM ChatGPT to Evernote 自動同期スクリプト起動バッチファイル
REM このファイルをダブルクリックするか、スタートアップに配置して自動起動できます

echo ChatGPT to Evernote 自動同期スクリプトを起動しています...
echo.

REM スクリプトのディレクトリに移動
cd /d "%~dp0"

REM 仮想環境が存在する場合はアクティベート
if exist "venv\Scripts\activate.bat" (
    echo 仮想環境をアクティベートしています...
    call venv\Scripts\activate.bat
)

REM .envファイルの存在確認
if not exist ".env" (
    echo [エラー] .env ファイルが見つかりません。
    echo .env.example を .env にコピーして、設定を行ってください。
    echo.
    pause
    exit /b 1
)

REM Pythonスクリプトを実行
echo スクリプトを実行しています...
python main.py

REM エラーが発生した場合
if errorlevel 1 (
    echo.
    echo [エラー] スクリプトの実行中にエラーが発生しました。
    echo ログファイルを確認してください。
    echo.
    pause
)
