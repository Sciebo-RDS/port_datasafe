from flask import jsonify
from RDS import FileTransferMode, LoginMode

def index():
    data = {
        "fileTransferArchive":"zip",
        "fileTransferMode":FileTransferMode.passive.value,
        "loginMode":LoginMode.credentials.value,
        "credentials": {
            "userId":False,
            "password":False
        }
    }
    return jsonify(data)
