# coding: utf-8

import os
from flask import request, abort, jsonify
from flask_api import FlaskAPI, status
from functools import wraps
import re
import requests
import logging

from reco_label import detect_label 

# Build app
app = FlaskAPI(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# Read auths file
APPKEYS = {}
if not os.path.exists("auths.txt"):
    app.logger.error("auths.txt file not found")
    exit(0)
with open("auths.txt", mode="r") as f:
    for line in f:
        if len(line) > 8 and ":" in line and line[0] != "#":
            key = line.split("#")[0].split(":")[0]
            ip = line.split("#")[0].split(":")[1]
            # remove "\n" if present
            if ip[-1] == "\n":
                ip = ip[:-1]
            if key in APPKEYS:
                APPKEYS[key].append(ip)
            else:
                APPKEYS[key] = [ip]

# Django URL Check Regex
url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

ip_regex = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}|\*\.\d{1,3}|\*')

def check_ip(ip, ip_to_test):
    if not re.match(ip_regex, ip):
        return False
    ip_truncated = "".join(ip_to_test.split("*")[0])
    ip = ip[0:len(ip_truncated)]
    if ip_truncated == ip:
        return True
    return False

# AUTH decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        # Necessary because of Nginx reverse proxy
        if request.environ.get("HTTP_X_FORWARDED_FOR") is None:
            ip = request.environ["REMOTE_ADDR"]
        else:
            ip = request.environ["HTTP_X_FORWARDED_FOR"]
        try:
            key = str(request.args.get("key"))
        except:
            return jsonify({"message": "BAD_REQUEST"}), \
                    status.HTTP_400_BAD_REQUEST
        for key_to_test in APPKEYS:
            for i, ip in enumerate( APPKEYS[key_to_test]):
                if key and key == key_to_test and check_ip(ip, APPKEYS[key_to_test][i]):
                 return view_function(*args, **kwargs)
                else:
                    continue
        return jsonify({"message": "UNAUTHORIZED"}), \
                status.HTTP_401_UNAUTHORIZED
    return decorated_function

def is_url_image(image_url):
   image_formats = ("image/png", "image/jpeg", "image/jpg")
   r = requests.head(image_url)
   if r.headers["content-type"] in image_formats:
      return True
   return False


# Define route to API
@app.route("/api/", methods=["GET"])
@require_appkey
def handle_requests():
    if request.method == "GET":
        # Read request's data
        try:
            url = str(request.args.get("source"))
        except (ValueError, TypeError):
            url = ""
        try:
            threshold = float(request.args.get("confidence"))
            if threshold > 100 or threshold < 0:
                raise ValueError
        except (ValueError, TypeError):
            threshold = 65
        try:
            fileout = bool(int(request.args.get("fileout")))
        except (ValueError, TypeError):
            fileout = True
        try:
            debug = bool(int(request.args.get("debug")))
        except (ValueError, TypeError):
            debug = False
        # Check if data is not empty and well formated
        if len(url) and url != "None" and re.match(url_regex, url):
            # Check if url actually points to an image
            if is_url_image(url):
                try:
                    # Process image
                    results = detect_label(url, threshold, fileout, debug)
                except:
                    app.logger.error("error processing image %s" % url)
                    return jsonify({"message": "DETECTOR_ERROR"}), \
                        status.HTTP_500_INTERNAL_SERVER_ERROR
            else:
                app.logger.info("BAD_CONTENT")
                return jsonify({"message": "BAD_CONTENT"}), \
                        status.HTTP_204_NO_CONTENT
            # send results
            app.logger.info("ip %s key %s masked image %s with threshold %f with fileout %s and debug %s" % (ip, key, url, threshold, fileout, debug))
            for result in results:
                try:
                    results[result] = request.host_url + "results/" + results[result]
                except TypeError:
                    pass
            results["status"] = "OK"
            return jsonify(results), status.HTTP_200_OK
        else:
            app.logger.info("NO_CONTENT")
            return jsonify({"message": "NO_CONTENT"}), \
                    status.HTTP_204_NO_CONTENT

if __name__ == "__main__":            
    # Build app
    app.run(debug=False, port=8000)
