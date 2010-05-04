@echo off
set MY_ROOT=%~dp0

del /f/s/q %MY_ROOT%\..\*.pyc > nul 2>&1
del /f/s/q %MY_ROOT%\..\build %MY_ROOT%\..\dist %MY_ROOT%\..\pip.egg-info> nul 2>&1
rmdir /s/q %MY_ROOT%\..\build %MY_ROOT%\..\dist %MY_ROOT%\..\pip.egg-info> nul 2>&1

del /f/s/q e:\clean > nul 2>&1
rmdir /s/q e:\clean > nul 2>&1

rem ### avoid overgrown PATH ###
rem ### this didn't seem to really work ###
rem set "strip_path=%PATH%;"

rem set "strip_path=%strip_path:C:\Python26\Scripts;=%"
rem set "strip_path=%strip_path:C:\Python26\;=%"
rem set "strip_path=%strip_path:E:\clean\Scripts;=%"
rem set "strip_path=%strip_path:C:\msysgit\bin;=%"
rem set "strip_path=%strip_path:C:\msysgit\mingw\bin;=%"

rem set "strip_path=%strip_path:;;=;%"

rem ### instead, hard-reset the path to our default ###
set "PATH=C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\system32\WindowsPowerShell\v1.0;C:\Program Files (x86)\Subversion\bin;C:\Program Files (x86)\TortoiseHg\;C:\Program Files (x86)\Bazaar"


set "PATH=C:\Python26\Scripts;C:\Python26;%PATH%"
virtualenv --no-site-packages --unzip-setuptools e:\clean
set "PATH=E:\clean\Scripts;%PATH%"
easy_install virtualenv
easy_install nose

set "PATH=%PATH%;C:\msysgit\bin;C:\msysgit\mingw\bin"

python -i c:\python26\scripts\nosetests-script.py -s -v %*


