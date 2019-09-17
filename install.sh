#!/bin/bash
# system dep
sudo apt-get install python3-dev python3-setuptools python3-pip python3-venv nginx supervisor -y
# check python/pip versions
if python -c 'import sys; exit(1) if sys.version_info.major < 3 and sys.version_info.minor < 5 else exit(0)';
then exit
fi
# build and activate virtual env
python3 -m venv env
source ~/detect_label/env/bin/activate
# app dependencies
pip3 install -r requirements.txt

# supervisor and Nginx config files
sudo python3 set_configs.py
sudo supervisorctl reread
sudo service supervisor restart
sudo nginx -t
sudo service nginx restart
# results/log folder
sudo mkdir -p /var/www/detect_label/results/
sudo chown $USER /var/www/detect_label/results/
sudo mkdir -p /var/log/detect_label/