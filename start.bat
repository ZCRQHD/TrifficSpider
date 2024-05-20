
source ./venv/bin/activate
cd publicTriffic
git pull origin master:master
python3 startBus.py
pause
python3 startBaidu.py
