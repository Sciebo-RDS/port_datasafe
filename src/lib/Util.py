from functools import wraps
from flask import request, g, current_app, abort
import os
import requests
import logging
from pyld import jsonld
import json

logger = logging.getLogger()


def loadAccessToken(userId: str, service: str) -> str:
    # FIXME make localhost dynamic for pactman
    tokenStorageURL = os.getenv(
        "USE_CASE_SERVICE_PORT_SERVICE", "http://localhost:3000"
    )
    # load access token from token-storage
    result = requests.get(
        f"{tokenStorageURL}/user/{userId}/service/{service}",
        verify=(os.environ.get("VERIFY_SSL", "True") == "True"),
    )

    if result.status_code > 200:
        return None

    access_token = result.json()
    logger.debug(f"got: {access_token}")

    if "type" in access_token and access_token["type"].endswith("Token"):
        username = access_token["data"]["user"]["data"]["username"]
        access_token = access_token["data"]["access_token"]

    logger.debug(
        "userId: {}, token: {}, service: {}".format(username, access_token, service)
    )

    return username, access_token


def require_api_key(api_method):
    @wraps(api_method)
    def check_api_key(*args, **kwargs):
        g.zenodo = None

        try:
            req = request.get_json(force=True, cache=True)
        except:
            req = request.form.to_dict()

        apiKey = req.get("apiKey")
        userId = req.get("userId")

        logger.debug("req data: {}".format(req))

        if apiKey is None and userId is not None:
            apiKey = loadAccessToken(userId, "Owncloud")

        if apiKey is None:
            logger.error("apiKey or userId not found.")
            abort(401)

        logger.debug("found apiKey")
        g.apiKey = apiKey

        return api_method(*args, **kwargs)

    return check_api_key


def from_jsonld(jsonld_data):
    if jsonld_data is None:
        return

    try:
        frame = json.load(open("src/lib/fdatasafe.jsonld"))
    except:
        frame = json.load(open("lib/fdatasafe.jsonld"))

    done = jsonld.frame(jsonld_data, frame)
    logger.debug("after framing: {}".format(done))

    
    done["titles"] = [{"title": done["name"]}]
    del done["name"]

    done["publicationYear"] = {
            "dateTime": done["datePublished"],
            "dateTimeScheme": "COMPLETE_DATE",
            "dateType": "Submitted"
        }
    del done["datePublished"]  

    if not isinstance(done["creator"], list):
        done["creator"] = [done["creator"]]

    done["creators"] = []

    for creator in done["creator"]:
        data = {
            "entityType": "Personal",
            "entityName": creator["name"]
        }
        data.update(creator)
        done["creators"].append(data)

    del done["creator"]

    done["publisher"] = {
        "entityName": done["creators"][0]["affiliation"]["name"],
        "entityType": "Organizational"
    }

    if done["resource"].find("/") > 0:
        typ, subtyp = tuple(done["resource"].split("/", 1))
        done["resource"] = typ
        done["resourceType"] = subtyp

    done["description"] = done["description"].replace("\n", "<br>")
    done["descriptions"] = [done["description"]]
    del done["description"]

    logger.debug("after transforming: {}".format(done))

    try:
        del done["@context"]
        del done["@id"]
        del done["@type"]
    except:
        pass

    return done