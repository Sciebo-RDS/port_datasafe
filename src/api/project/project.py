import logging
import os
from flask import jsonify, request, g, current_app
from werkzeug.exceptions import abort
from lib.Util import require_api_key, from_jsonld


logger = logging.getLogger()


@require_api_key
def index():
    pass


@require_api_key
def get(project_id):
    pass


@require_api_key
def post():
   pass


@require_api_key
def delete(project_id):
    pass


@require_api_key
def patch(project_id):
    pass


@require_api_key
def put(project_id):
    pass
