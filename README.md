# How to run by script

Just double-click on `run_script.bat` to launch the UI.

# How to run manually for the first time

Just run these commands to launch UI:

```batch
python -m venv virtual_env
virtual_env\Scripts\activate.bat
pip install tk
pip install pandas
python -m pip install --upgrade pip
pip freeze > requirements.txt
python script.py
```
