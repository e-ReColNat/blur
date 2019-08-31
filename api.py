from flask import request, abort
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
        if request.args.get('key') and \
           request.args.get('key') in APPKEYS and \
           ip == APPKEYS[request.args.get('key')]:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

# Define route to API
@app.route("/", methods=['GET', 'POST'])
@require_appkey
def handle_requests():
    if request.method == 'POST':
        req = str(request.data.get('text', ''))
        # Process POST request and send response
        if len(req):
            return req, status.HTTP_200_OK
        else:
            return req, status.HTTP_204_NO_CONTENT
    else:
        # Process GET requests
        req = {'request data': request.data}
        return req

if __name__ == "__main__":
    # Build app
    app.run(debug=True)
