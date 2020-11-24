from flask import jsonify


def index():
    data = {
        "fileTransferArchive":False,
        "fileTransferMode":1,
        "credentials": {
            "userId":True,
            "password":True
        }
    }
    return jsonify(data)
