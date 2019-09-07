#!/bin/bash
source ~/detect_label/env/bin/deactivate
rm -r env
sudo rm /etc/nginx/conf.d/virtual.conf
sudo rm /etc/supervisor/conf.d/detect_label.conf