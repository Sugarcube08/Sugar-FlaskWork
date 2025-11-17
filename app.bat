@echo off
REM Windows launcher for the uv script

REM %~dp0 expands to the directory of this .bat file
REM Run the corresponding script (no extension) through uv
uv run --script "%~dp0app" %*
