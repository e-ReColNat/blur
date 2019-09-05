#!/bin/sh
sudo apt-get install nginx supervisor python3-pip python3-venv
#python3 -m venv env
#source ./env/bin/activate
#pip3 install -r requirements.txt
#
#echo "[program:detect_label]
#directory=/home/admindetect/detect_label
#command=/home/admindetect/detect_label/env/bin/gunicorn api:app -b localhost:8000
#autostart=true
#autorestart=true
#stderr_logfile=/var/log/detect_label/detect_label.err.log
#stdout_logfile=/var/log/detect_label/detect_label.out.log" > /etc/supervisor/conf.d
#sudo supervisorctl reread
#sudo service supervisor restart
#
#echo "server {
#    listen       80;
#    server_name  detectlabel.agoralogie.fr;
#
#    location / {
#        proxy_pass http://127.0.0.1:8000;
#    }
#}" > /etc/nginx/conf.d/virtual.conf
#
#sudo nginx -t
#sudo service nginx restart