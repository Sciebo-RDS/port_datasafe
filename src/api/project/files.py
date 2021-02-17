import logging
import os
import json
import requests
from RDS import Util
from lib.datasafe import Datasafe
from flask import jsonify, request, g, abort
from io import BytesIO, BufferedReader

logger = logging.getLogger()


# FIXME: all endpoints need server tests, but POST cannot currently be tested through pactman, because it only supports json as content type
def index(project_id):
    abort(500)


def get(project_id, file_id):
    abort(500)


def post(project_id):
    # trigger upload on datasafe
    try:
        req = request.get_json(force=True, cache=True)
    except:
        req = request.form.to_dict()

    data = {
        "filepath": "{}/ro-crate-metadata.json".format(req["folder"]),
        "userId": req["userId"]
    }

    metadata = json.loads(
        BytesIO(
            requests.get(
                "http://circle1-{}/storage/file".format("port-owncloud"),
                json=data,
                verify=(os.environ.get("VERIFY_SSL", "True") == "True"),
            ).content
        )
        .read()
        .decode("UTF-8")
    )

    token = Util.loadToken(req["userId"], "port-datasafe")
    email = token.user.username
    password = token.access_token

    datasafe = Datasafe(
        email,
        password,
        metadata,
        req["folder"],
        os.getenv("DATASAFE_PUBLICKEY"),
        os.getenv("DATASAFE_PRIVATEKEY")
    )

    logger.debug("Trigger file upload")
    datasafe.triggerUploadForProject()
    logger.debug("Finished trigger")

    return jsonify({"success": True}), 200


def patch(project_id, file_id):
    abort(500)


def delete(project_id, file_id=None):
    abort(500)
