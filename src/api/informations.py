from flask import jsonify
from RDS import FileTransferMode, LoginMode

def index():
    data = {
        "fileTransferArchive":False,
        "fileTransferMode":FileTransferMode.passive,
        "loginMode":LoginMode.credentials,
        "credentials": {
            "userId":True,
            "password":True
        }
    }
    return jsonify(data)
