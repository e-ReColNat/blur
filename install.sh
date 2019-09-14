#!/bin/bash
# system dep
sudo apt-get install python3-dev python3-setuptools python3-pip python3-venv nginx supervisor -y
# build and activate virtual env
python3 -m venv env
source ~/detect_label/env/bin/activate
# app dep
pip3 install -r requirements.txt
# supervisor and Nginx config files

sudo cp detect_label.conf /etc/supervisor/conf.d/.
sudo supervisorctl reread
sudo service supervisor restart
sudo cp virtual.conf /etc/nginx/conf.d/.
sudo nginx -t
sudo service nginx restart
# results folder
sudo mkdir /var/www/detect_label/results/
sudo chown $USER /var/www/detect_label/results/
