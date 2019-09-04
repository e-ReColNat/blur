from flask import request, abort, jsonify
from flask_api import FlaskAPI, status
from functools import wraps
import re
import requests

from auths import APPKEYS
from Detector.reco_michel import detect_label 

# Build app
app = FlaskAPI(__name__)

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
        ip = request.remote_addr
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
            url = str(request.data.get("Data"))
        except ValueError:
            url = ""
        # Check if data is not empty and well formated
        if len(url) and url != "None" and re.match(url_regex, url):
            # Check if url actually points to an image
            if is_url_image(url):
                # Process image
                result_url, result_list = detect_label(url)
                # TODO process response
            else:
                return jsonify({"message": "BAD_CONTENT"}), \
                        status.HTTP_204_NO_CONTENT
            return jsonify({"message": "OK", \
                            "result_url": result_url, \
                            "result_list": result_list}), \
                            status.HTTP_200_OK
        else:
            return jsonify({"message": "NO_CONTENT"}), \
                    status.HTTP_204_NO_CONTENT

if __name__ == "__main__":
    # Build app
    app.run(debug=False, port=8000)
