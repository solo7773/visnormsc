@echo off
title Run visnormsc
echo Beware your working directory is:
echo %cd%
echo\ 
echo This is the default place where the program will save temporary data.
echo\
echo When you are ready.
pause
python ../ncgui.py

if NOT %ERRORLEVEL% == 0 (
    echo\
    echo python cannot be found, please make sure you have installed python correctly and the path to python has been added to the environment variable PATH.
    echo Error occurs. Please exit and fix it.
    echo\
) ELSE (
    echo\
    echo Everything is ok. You can exit the program now.
    echo\
)
pause