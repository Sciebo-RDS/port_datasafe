import requests
import jwt
from requests_jwt import JWTAuth, payload_path, payload_method, payload_body

class Datasafe():
    def __init__(self, email, token, folder, public_key, private_key, address=None):
        self.email = email
        if "@" not in self.email:
            raise ValueError("email not valid.")

        self.token = token
        self.folder = folder
        self.address = address or "https://datasafe-dev.uni-muenster.de"

        if self.folder.endsWith("/"):
            self.folder = self.folder[:-1]
        
        if not self.folder.startsWith("/"):
            self.folder = "/" + self.folder

        self.metadata = None

        self.public_key = public_key
        self.private_key = private_key

        auth = JWTAuth(self.private_key, alg='HS256')

        auth.add_field("iss", "https://www.ulb.uni-muenster.de")
        auth.add_field("sub", "24400320")
        auth.add_field("upn", self.email)
        auth.add_field("aud", "wallet")
        auth.add_field("preferred_username", self.email.split("@")[0])
        auth.add_field("groups", ["RegistrationManager", "ds-user"])

        self._session = requests.Session()
        self._session.auth = auth

    def setMetadata(self, metadata):
        # TODO: transform json-ld to datasafe
        self.metadata = metadata

        return self

    def getProjects(self):
        pass

    def getProject(self, id):
        pass

    def createProject(self, title):
        pass

    def deleteFilesInProject(self, id):
        pass

    def triggerFileForProject(self, id):
        if self.metadata is None:
            raise ValueError("metadata is not set.")

        data = {
            "accessInfo": {
                "directory": self.folder,
                "port": 443,
                "protocol": "WEBDAV",
                "serverName": "https://sciebords.uni-muenster.de",
                "token": "Bearer {}".format(self.token)
            },
            "metadata": self.metadata
        }

        req = self._session.get("{}/big-file-transfer/api/v1/transfer/start".format(self.address), data=data)

        return jwt.decode(req.text(), self.public_key, algorithms='HS256')