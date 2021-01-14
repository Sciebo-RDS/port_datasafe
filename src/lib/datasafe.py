import requests
import jwt
from requests_jwt import JWTAuth, payload_path, payload_method, payload_body
from lib.Util import from_jsonld, loadAccessToken

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

        auth = JWTAuth(self._private_key, alg='HS256')

        metadata = from_jsonld(metadata)

        self._metadata = {
            "dataCiteMetadata": metadata,
            "administrativeMetadata": {
                "authorizedPersons": [metadata["creators"][0]],
                "curatingPersons": [metadata["creators"][0]],
                "dataSupplier": [metadata["creators"][0]]
            }
        }

        auth.add_field("iss", "https://www.ulb.uni-muenster.de")
        auth.add_field("sub", "24400320")
        auth.add_field("upn", self.email)
        auth.add_field("aud", "wallet")
        auth.add_field("preferred_username", self.email.split("@")[0])
        auth.add_field("groups", ["RegistrationManager", "ds-user"])

        self._session = requests.Session()
        self._session.auth = auth

    @property
    def metadata(self):
        return self._metadata
    
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

        req = self._session.get("{}/big-file-transfer/api/v1/transfer/start".format(self.address), data=data)

        return jwt.decode(req.text(), self._public_key, algorithms=self._session.auth.alg)