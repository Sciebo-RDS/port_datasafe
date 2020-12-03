import logging
import os
import json
import requests
from lib.Util import loadAccessToken
from lib.datasafe import Datasafe
from flask import jsonify, request, g, abort
from io import BytesIO, BufferedReader

logger = logging.getLogger()


# FIXME: all endpoints need server tests, but POST cannot currently be tested through pactman, because it only supports json as content type
@require_api_key
def index(project_id):
    return jsonify(g.osf.project(project_id).storage().files)


@require_api_key
def get(project_id, file_id):
    fileslist = list(g.osf.project(project_id).storage().files)
    return jsonify(fileslist[file_id])


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

    token = loadAccessToken(req["userId"], "Owncloud")
    url = os.getenv("OWNCLOUD_INSTALLATION_PATH")
    url = "{}/index.php/apps/rds/mailAddress".format(url)

    headers = {"Authorization": "Bearer {}".format(token)}
    email = request.get(url, headers=headers).json().get("email")

    datasafe = Datasafe(
        email,
        token,
        req["folder"],
        os.getenv("DATASAFE_PUBLICKEY"),
        os.getenv("DATASAFE_PRIVATEKEY")
    )

    logger.debug("Trigger file upload")
    datasafe.triggerUploadForProject()
    logger.debug("Finished trigger")

    return jsonify({"success": True}), 200


@require_api_key
def patch(project_id, file_id):
    raise NotImplementedError()


@require_api_key
def delete(project_id, file_id=None):
    if file_id is None:
        try:
            for file in g.osf.project(project_id).storage().files:
                file.remove()

            return "", 200
        except:
            return abort(500)

    raise NotImplementedError()
