from connexion_plus import App, MultipleResourceResolver, Util

import json
import requests
from werkzeug.exceptions import abort

import logging
import os

log_level = os.environ.get("LOGLEVEL", "DEBUG")
logging.getLogger().handlers = []
logging.basicConfig(format="%(asctime)s %(message)s", level=log_level)
logger = logging.getLogger()


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

app = bootstrap("PortDatasafe", all=True)
