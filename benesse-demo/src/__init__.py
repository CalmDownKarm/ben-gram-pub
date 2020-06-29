import os

from flask import Flask
from werkzeug.exceptions import HTTPException, default_exceptions

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.logger.info('Flask app created')
    return app

app = create_app()

def handle_error(error):
    if isinstance(error, HTTPException):
        return jsonify(message=error.description, code=error.code)
    return jsonify(message='An error occured', code=500)

for exc in default_exceptions:
    app.register_error_handler(exc, handle_error)

from .api import *

app.register_blueprint(api)
app.add_template_global(name='version', f='1.0')
