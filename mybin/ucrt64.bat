@echo off
set "MINGW_PATH=D:\msys64\ucrt64"
set PATH=%MINGW_PATH%\bin;%MINGW_PATH%\opt\bin;%PATH%;
 
set C_INCLUDE_PATH=%MINGW_PATH%/include;%MINGW_PATH%/include/SDL2
set CPLUS_INCLUDE_PATH=%MINGW_PATH%/include;%MINGW_PATH%/include/SDL2
set LIBRARY_PATH=%MINGW_PATH%/lib

echo ucrt64环境设置完毕
