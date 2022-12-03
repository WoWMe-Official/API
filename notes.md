## setup
```
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## setup if you have multiple versions of python installed
```
pip install virtualenv
# py -m virtualenv -p="C:\Users\thear\AppData\Local\Programs\Python\Python310\python.exe" venv
py -m virtualenv -p="<path to your python.exe>" venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

# if the interpreter does not recognize imports, for some reason, use:
ctrl + shift + P > select python interpreter
strl + shift + ` > should work now

# for saving & upgrading
```
venv\Scripts\activate
call pip freeze > requirements.txt
powershell "(Get-Content requirements.txt) | ForEach-Object { $_ -replace '==', '>=' } | Set-Content requirements.txt"
call pip install -r requirements.txt --upgrade
call pip freeze > requirements.txt
powershell "(Get-Content requirements.txt) | ForEach-Object { $_ -replace '>=', '==' } | Set-Content requirements.txt"
```
