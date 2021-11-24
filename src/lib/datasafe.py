import requests
import logging
import time
from .requests_jwt import JWTAuth

logger = logging.getLogger()


def parse_rocrate(res, email):
    creator = []

    if not isinstance(res["creator"], list):
        res["creator"] = [res["creator"]]

    for c in res["creator"]:
        if isinstance(c, str):
            creator.append({
                "name": c
            })
        else:
            creator.append(c)

    creators = [{
        "entityName": c["name"],
        "entityType": "Personal",
        "dateOfBirth": "",
    } for c in creator]

    templCreator = []
    for c in creators:
        splitName = c["entityName"].split(" ", 1)
        acc = email.split("@")[0]

        c.update({
            "account": acc,
            "entityName": "{}, {}".format(splitName[1], splitName[0]),
            "familyName": splitName[1],
            "givenName": splitName[0],
            "emailAddress": email,
            "local": True,
            "nameIdentifiers": [],
            "salutation": "Herr"
        })

        templCreator.append(c)
    creators = templCreator

    result = {
        "description": res["description"].replace("\n", "<br>"),
        "creators": creators,
        "contributors": creators,
        "doi": {
            "identifierType": "DOI",
            "value": ""
        },
        "publicationYear": {
            "dateTime": res["datePublished"],
            "dateTimeScheme": "COMPLETE_DATE",
            "dateType": "Submitted"
        },
        "publisher": {
            "entityName": creator[0]["affiliation"],
            "entityType": "Organizational"
        },
        "resource": {
            "resource": "Research data",
            "resourceType": "Dataset"
        },
        "titles": [{"title": res["name"]}],
    }

    """ # Disable this part, maybe use it later for new profileschemas
    if res["zenodocategory"].find("/") > 0:
        typ, subtyp = tuple(res["zenodocategory"].split("/", 1))
        result["resource"] = {
            "resource": typ,
            "resourceType": subtyp
        } """

    return result


class Datasafe():
    def __init__(self, email, token, metadata, folder, public_key, private_key, address=None):
        self.email = email
        if "@" not in self.email:
            raise ValueError("email not valid.")

        self.token = token
        self.folder = folder
        self.address = address or "https://datasafe-dev.uni-muenster.de"

        if str(self.folder).endswith("/"):
            self.folder = self.folder[:-1]

        if not str(self.folder).startswith("/"):
            self.folder = "/" + self.folder

        self._public_key = public_key
        self._private_key = private_key

        auth = JWTAuth(self._private_key, alg='RS256',
                       header_format="Bearer %s")

        metadata = parse_rocrate(metadata, email)

        handle = {
            "identifierType": "Handle",
            "value": self.get_handle()
        }

        metadata["doi"] = handle
        metadata["handle"] = handle

        self._metadata = {
            "dataCiteMetadata": metadata,
            "administrativeMetadata": {
                "acceptedAGBVersion": "string",
                "bagitPrefix": "wwurdm/",
                "completeSize": 0,
                "authorizedPersons": [metadata["creators"][0]],
                "curatingPersons": [metadata["creators"][0]],
                "dataSupplier": metadata["creators"][0],
                "ingestDate": metadata["publicationYear"],
                "fileMetadataList": [],
                "identifier": {"identifierType": "DOI", "value": ""},
            }
        }

        auth.add_field("iss", "https://www.ulb.uni-muenster.de")
        auth.add_field("sub", "24400320")
        auth.add_field("upn", self.email)
        auth.add_field("aud", "wallet")
        auth.add_field("preferred_username", self.email.split("@")[0])
        auth.add_field("groups", ["RegistrationManager", "ds-user"])
        auth.add_field("nbf", int(time.time()))
        auth.expire(60*5)

        self._session = requests.Session()
        self._session.auth = auth

    @property
    def metadata(self):
        return self._metadata

    def get_handle(self, prefix="sciebords"):
        data = {
            "prefix": prefix
        }
        req = requests.get(
            "{}/generator-service/api/v1/niss".format(self.address), params=data)
        return "{}/{}".format(prefix, req.text)

    def triggerUploadForProject(self):
        if self._metadata is None or not isinstance(self._metadata, dict):
            raise ValueError("metadata is not set.")

        data = {
            "accessInfo": {
                "directory": self.folder,
                "port": 443,
                "protocol": "WEBDAV",
                "serverName": "https://sciebords.uni-muenster.de",
                "token": "Bearer {}".format(self.token)
            },
            "metadata": self._metadata
        }

        logger.debug("send data: {}".format(data))

        req = self._session.post(
            "{}/big-file-transfer/api/v1/transfer/start".format(self.address), json=data)
        logger.debug("got datasafe content: {}".format(req.content))

        return req.status_code < 300
