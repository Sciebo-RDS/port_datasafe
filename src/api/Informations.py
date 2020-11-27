from flask import jsonify
from RDS import FileTransferMode, LoginMode

def index():
    data = {
        "fileTransferArchive":"zip",
        "fileTransferMode":FileTransferMode.passive,
        "loginMode":LoginMode.credentials,
        "credentials": {
            "userId":False,
            "password":False
        }
    }
    return jsonify(data)
