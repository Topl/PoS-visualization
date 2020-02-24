import api
from flask import escape

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    message = None
    api_version = None
    adversary = None
    slider_max = None
    w = None

    request_json = request.get_json()
    request_args = request.args

    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '-',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Authorization',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'
        }
        return ('', 204, headers)

    # Set CORS headers for main requests
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }

    # if request.args and 'message' in request.args:
    #     message request.args.get('message')
    if request_json and 'message' in request_json:
        message = request_json['message']

        if message is None or "w" not in message or "slider_max" not in message:
            # Bad request
            return f"The request json must contain two fields: 'w' and 'slider_max'"
    
        # finally
        w = message["w"]
        slider_max = message["slider_max"]
        if "api_version" in message:
            api_version = message["api_version"]
        if "adversary" in message:
            adversary = message["adversary"]

    else:
        if request_args and 'w' in request_args:
            w = escape(request_args['w'])
        else:
            return f"'w' field not found in request"

        if request_args and 'slider_max' in request_args:
            slider_max = escape(request_args['slider_max'])
        else: 
            return f"'slider_max' field not found in request"

        if request_args and 'api_version' in request_args:
            api_version = escape(request_args['api_version'])

        if request_args and 'adversary' in request_args:
            adversary = escape(request_args['adversary'])

    return (api.build_fork(
        w = w, 
        slider_max = slider_max, 
        api_version = api_version,
        adv_type = adversary
    ), 200, headers)
