@echo off
echo Installing requirements...
pip install -r requirements.txt

echo Creating application icon...
python create_icon.py

echo Building executable...
pyinstaller wav_converter.spec --clean

echo Build complete!
pause
