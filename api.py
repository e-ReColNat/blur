# coding: utf-8

from flask import request, abort, jsonify
from flask_api import FlaskAPI, status
from functools import wraps
import re
import requests
import logging

from reco_michel import detect_label 

HOST = "http://detectlabel.agoralogie.fr/"

# Build app
app = FlaskAPI(__name__)

gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

# Read auths file
APPKEYS = {}
with open("auths.txt", mode="r") as f:
    for line in f:
        if len(line) > 8 and ":" in line and line[0] != "#":
            key = line.split("#")[0].split(":")[0]
            ip = line.split("#")[0].split(":")[1]
            # remove "\n" if present
            if ip[-1] == "\n":
                ip = ip[:-1]
            APPKEYS[key] = ip

# Django URL Check Regex
url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

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
        key = request.headers.get("Key")
        if key and key in APPKEYS and ip == APPKEYS[key]:
            return view_function(*args, **kwargs)
        elif not key or key not in APPKEYS:
            return jsonify({"message": "UNAUTHORIZED KEY"}), \
                    status.HTTP_401_UNAUTHORIZED
        elif ip != APPKEYS[key]:
            return jsonify({"message": "UNAUTHORIZED IP"}), \
                    status.HTTP_401_UNAUTHORIZED
    return decorated_function

def is_url_image(image_url):
   image_formats = ("image/png", "image/jpeg", "image/jpg")
   r = requests.head(image_url)
   if r.headers["content-type"] in image_formats:
      return True
   return False


# Define route to API
@app.route("/api/", methods=["POST"])
@require_appkey
def handle_requests():
    if request.method == "POST":
        # Read request's data
        try:
            url = str(request.data.get("data"))
        except (ValueError, TypeError):
            url = ""
        try:
            threshold = float(request.data.get("threshold"))
        except (ValueError, TypeError):
            threshold = 0.65
        try:
            debug = bool(request.data.get("debug"))
        except (ValueError, TypeError):
            debug = False
        # Check if data is not empty and well formated
        if len(url) and url != "None" and re.match(url_regex, url):
            # Check if url actually points to an image
            if is_url_image(url):
                # Process image
                try:
                    sensored_img, result_data = detect_label(url, threshold, debug)
                except:
                    app.logger.error("error processing image %s" % url)
                    return jsonify({"message": "DETECTOR_ERROR"}), \
                        status.HTTP_500_INTERNAL_SERVER_ERROR
                app.logger.info("masked image %s" % url)
            else:
                return jsonify({"message": "BAD_CONTENT"}), \
                        status.HTTP_204_NO_CONTENT
            return jsonify({"message": "OK", \
                            "result_image": HOST + sensored_img, \
                            "result_data": HOST + result_data}), \
                            status.HTTP_200_OK
        else:
            return jsonify({"message": "NO_CONTENT"}), \
                    status.HTTP_204_NO_CONTENT

if __name__ == "__main__":            
    # Build app
    app.run(debug=False, port=8000)
