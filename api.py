from flask import request, abort, jsonify
from flask_api import FlaskAPI, status
from functools import wraps
from urllib.parse import urlparse

from auths import APPKEYS

# Build app
app = FlaskAPI(__name__)

# AUTH decorator function
def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        key = request.headers.get("Key")
        if key and \
           key in APPKEYS and \
           ip == APPKEYS[key]:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"message": "UNAUTHORIZED"}), status.HTTP_401_UNAUTHORIZED
    return decorated_function

# Define route to API
@app.route("/api/", methods=["GET", "POST"])
@require_appkey
def handle_requests():
    if request.method == "POST":
        req = str(request.data.get("Data"))
        # Process POST request
        if len(req) and req != "None":
            return jsonify({"req": req, "message": "OK"}), status.HTTP_200_OK
        else:
            return jsonify({"message": "NO_CONTENT"}), status.HTTP_204_NO_CONTENT
    else:
        req = str(request.data.get("Data"))
        # Process GET requests
        if len(req) and req != "None":
            return jsonify({"req": req, "message": "OK"}), status.HTTP_200_OK
        else:
            return jsonify({"message": "NO_CONTENT"}), status.HTTP_204_NO_CONTENT

if __name__ == "__main__":
    # Build app
    app.run(debug=True)
