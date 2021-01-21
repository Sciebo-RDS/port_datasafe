from connexion_plus import App, MultipleResourceResolver, Util

import json
import requests
from werkzeug.exceptions import abort

import logging
import os

log_level = os.environ.get("LOGLEVEL", "DEBUG")
logger = logging.getLogger("")
logging.getLogger("").handlers = []
logging.basicConfig(format="%(asctime)s %(message)s", level=log_level)


def bootstrap(name="MicroService", *args, **kwargs):
    list_openapi = Util.load_oai(
        os.getenv(
            "OPENAPI_MULTIPLE_FILES",
            "../../circle2_use_cases/interface_port_metadata.yml"
        )
    )

    osf_address = None
    if "address" in kwargs:
        osf_address = kwargs["address"]
        del kwargs["address"]

    app = App(name, *args, **kwargs)

    for oai in list_openapi:
        app.add_api(
            oai,
            resolver=MultipleResourceResolver(
                "api", collection_endpoint_name="index"),
            validate_responses=True,
        )

    return app


def register_service(
    servicename: str
):
    tokenStorage = os.getenv("CENTRAL_SERVICE_TOKEN_STORAGE")
    if tokenStorage is None:
        return False

    data = {
        "servicename": servicename,
        "implements": ["metadata"],
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(
        f"{tokenStorage}/service",
        json=data,
        headers=headers,
        verify=(os.environ.get("VERIFY_SSL", "True") == "True"),
    )

    if response.status_code != 200:
        raise Exception(
            "Cannot find and register Token Storage, msg:\n{}".format(
                response.text)
        )

    response = response.json()
    if response["success"]:
        logger.info(
            f"Registering {servicename} in token storage was successful.")
        return True

    logger.error(
        f"There was an error while registering {servicename} to token storage.\nJSON: {response}"
    )

    return False


app = bootstrap("PortDatasafe", all=True)
