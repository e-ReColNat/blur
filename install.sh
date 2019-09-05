#!/bin/bash
sudo apt-get install python-setuptools nginx supervisor python3-pip python3-venv -y

python3 -m venv env
source ~/detect_label/env/bin/activate

pip3 install -r requirements.txt

sudo sh -c 'echo "[program:detect_label]\ndirectory=/home/admindetect/detect_label\ncommand=/home/admindetect/detect_label/env/bin/gunicorn api:app -b localhost:8000\nautostart=true\nautorestart=true\nstderr_logfile=/var/log/detect_label/detect_label.err.log\nstdout_logfile=/var/log/detect_label/detect_label.out.log" > /etc/supervisor/conf.d/detect_label.conf'
sudo supervisorctl reread
sudo service supervisor restart
sudo sh -c 'echo "server {\n    listen       80;\n    server_name  detectlabel.agoralogie.fr;\n\n    location / {\n        proxy_pass http://127.0.0.1:8000;\n    }\n}" > /etc/nginx/conf.d/virtual.conf'
sudo nginx -t
sudo service nginx restart