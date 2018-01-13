set home=%LOCALAPPDATA%\Programs\Python\Python36

echo %home%>venv\pyvenv.cfg
echo include-system-site-packages = false>>venv\pyvenv.cfg
echo version = 3.6.4>>venv\pyvenv.cfg


