@echo off
cd /d "%~dp0"
C:\PyPy\pypy3.10-v7.3.19-win64\pypy3.exe engine/uci.py --book engine/komodo.bin
