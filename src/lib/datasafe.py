class Datasafe():
    def __init__(self, username, token, folder, address=None):
        self.username = username
        self.token = token
        self.folder = folder
        self.address = address or "https://datasafe-dev.uni-muenster.de"

        if not self.folder.startsWith("/"):
            self.folder = "/" + self.folder

    def trigger_workflow(self):
        data = {
            "iss": "https://www.ulb.uni-muenster.de",
            "sub": "24400320",
            "upn": "tester@uni-muenster.de",
            "preferred_username": "tester",
            "aud": "wallet",
            "groups": [
                "RegistrationManager"
            ]
        }

        postData = {
            "accessInfo": {
                "directory": self.folder,
                "email": "email@domain.xy",
                "password": "password",
                "port": 443,
                "protocol": "WEBDAV",
                "serverName": "https://sciebords.uni-muenster.de",
                "token": "Bearer {}".format(self.token),
                "userId": self.username
            },
            "metadata": {}
        }