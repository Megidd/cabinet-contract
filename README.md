# How to run

## Run by script

Just double-click on `run_script.bat` to launch the UI.

## Run manually for the first time

Just run these commands to launch UI:

```batch
python -m venv virtual_env
virtual_env\Scripts\activate.bat
python -m pip install --upgrade pip
pip install tk
pip install pandas
pip freeze > requirements.txt
python script.py
```
