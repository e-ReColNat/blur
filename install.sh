#!/bin/sh
sudo apt-get install nginx supervisor python3-pip python3-virtualenv
python3 -m venv env
source ./env/bin/activate
pip3 install -r requirements.txt
touch /etc/supervisor/conf.d
echo "[program:detect_label]
directory=/home/admindetect/detect_label
command=/home/admindetect/detect_label/env/bin/gunicorn api:app -b localhost:8000
autostart=true
autorestart=true
stderr_logfile=/var/log/detect_label/detect_label.err.log
stdout_logfile=/var/log/detect_label/detect_label.out.log" > /etc/supervisor/conf.d
